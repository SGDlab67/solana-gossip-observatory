// S-NodeFinder wire spy: pull-only, non-voting Solana gossip observer.
//
// Joins the mainnet gossip mesh as a spy node (ephemeral ports, dummy
// contact info), continuously pulls CRDS data, and writes every
// first-seen ContactInfo record to timestamped JSONL under
// <out-dir>/<UTC-date>/spy-<UTC-time>.jsonl. A per-tick summary line
// (peer totals, validator count) goes to spy-summary-<UTC-time>.jsonl.
//
// Minimum viable instrument: ugly is fine, it only has to not stop.

use std::collections::HashSet;
use std::net::{SocketAddr, ToSocketAddrs};
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use solana_gossip::cluster_info::ClusterInfo;
use solana_gossip::gossip_service::make_node;
use solana_keypair::Keypair;
use solana_net_utils::{get_cluster_shred_version, SocketAddrSpace};
use solana_signer::Signer;

const ENTRYPOINTS: &[&str] = &[
    "entrypoint.mainnet-beta.solana.com:8001",
    "entrypoint2.mainnet-beta.solana.com:8001",
];
const TICK_MS: u64 = 30_000; // CRDS table poll interval
const FLUSH_EVERY_TICKS: u64 = 1;

fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

fn utc_stamp(now: u64) -> String {
    // Seconds since epoch -> UTC "YYYY-MM-DD" and "HHMMSS" without external deps.
    let days = now / 86400;
    let secs_of_day = now % 86400;
    // Civil-from-days (Howard Hinnant algorithm).
    let z = days as i64 + 719468;
    let era = if z >= 0 { z } else { z - 146096 } / 146097;
    let doe = (z - era * 146097) as i64;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if m <= 2 { y + 1 } else { y };
    let hh = secs_of_day / 3600;
    let mm = (secs_of_day % 3600) / 60;
    let ss = secs_of_day % 60;
    format!("{:04}-{:02}-{:02} {:02}:{:02}:{:02}", y, m, d, hh, mm, ss)
}

fn date_dir(now: u64) -> String {
    utc_stamp(now)[..10].to_string()
}

fn time_stamp(now: u64) -> String {
    utc_stamp(now).replace(':', "").replace(' ', "-")
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mut out_dir = PathBuf::from("data");
    let mut max_seconds: Option<u64> = None;
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--out-dir" => {
                i += 1;
                out_dir = PathBuf::from(&args[i]);
            }
            "--seconds" => {
                i += 1;
                max_seconds = Some(args[i].parse().expect("--seconds needs a number"));
            }
            other => {
                eprintln!("unknown arg: {other}");
                std::process::exit(2);
            }
        }
        i += 1;
    }

    let entrypoints: Vec<SocketAddr> = ENTRYPOINTS
        .iter()
        .filter_map(|e| (*e).to_socket_addrs().ok().and_then(|mut it| it.next()))
        .collect();
    if entrypoints.is_empty() {
        eprintln!("could not resolve any entrypoint");
        std::process::exit(1);
    }

    // Shred version: ask the entrypoint's ip_echo server; fall back to 8000,
    // then warn and use 0 (may be ignored by the mesh).
    let mut shred_version: u16 = 0;
    for port in [entrypoints[0].port(), 8000] {
        let probe = SocketAddr::new(entrypoints[0].ip(), port);
        match get_cluster_shred_version(&probe) {
            Ok(v) => {
                shred_version = v;
                break;
            }
            Err(e) => eprintln!("shred-version probe {probe} failed: {e}"),
        }
    }
    eprintln!("shred_version: {shred_version}");

    let keypair = Keypair::new();
    let exit = Arc::new(AtomicBool::new(false));
    let (gossip_service, _ip_echo, spy_ref) = make_node(
        keypair,
        &entrypoints,
        exit.clone(),
        None, // None -> spy_node: dummy ports, pull-only
        shred_version,
        true, // should_check_duplicate_instance
        SocketAddrSpace::new(false),
    );
    eprintln!(
        "Node Id: {} | entrypoints: {entrypoints:?} | gossip: {:?}",
        spy_ref.id(),
        spy_ref.my_contact_info().gossip(),
    );

    let start = now_unix();
    let day = date_dir(start);
    let stamp = time_stamp(start);
    let rec_dir = out_dir.join(&day);
    std::fs::create_dir_all(&rec_dir).expect("create output dir");
    let rec_path = rec_dir.join(format!("spy-{stamp}.jsonl"));
    let sum_path = rec_dir.join(format!("spy-summary-{stamp}.jsonl"));
    let rec_file = std::fs::File::create(&rec_path).expect("open records file");
    let sum_file = std::fs::File::create(&sum_path).expect("open summary file");
    let mut rec_writer = std::io::BufWriter::new(rec_file);
    let mut sum_writer = std::io::BufWriter::new(sum_file);

    let mut seen: HashSet<String> = HashSet::new();
    let mut ticks: u64 = 0;
    let mut total_new: u64 = 0;

    eprintln!("writing records to {}", rec_path.display());
    while max_seconds.map_or(true, |s| now_unix() - start < s) {
        std::thread::sleep(Duration::from_millis(TICK_MS));

        let peers = spy_ref.all_peers();
        let validator_set: HashSet<String> = spy_ref
            .tvu_peers(ContactInfo::clone)
            .iter()
            .map(|c| c.pubkey().to_string())
            .collect();
        let tick_at = now_unix();
        let mut new_this_tick = 0u64;

        for (contact, last_heard) in &peers {
            let pk = contact.pubkey().to_string();
            if !seen.insert(pk.clone()) {
                continue;
            }
            let rec = serde_json::json!({
                "observed_at": tick_at,
                "last_heard": last_heard,
                "pubkey": pk,
                "wallclock": contact.wallclock(),
                "shred_version": contact.shred_version(),
                "version": format!("{}", contact.version()),
                "gossip": contact.gossip().map(|a| a.to_string()),
                "rpc": contact.rpc().map(|a| a.to_string()),
                "tpu": contact.tpu().map(|a| a.to_string()),
                "tvu": contact.tvu().map(|a| a.to_string()),
                "validator": validator_set.contains(&pk),
            });
            let line = serde_json::to_string(&rec).expect("serialize record");
            let _ = writeln!(rec_writer, "{line}");
            new_this_tick += 1;
        }

        let summary = serde_json::json!({
            "tick_at": tick_at,
            "total_peers": peers.len(),
            "validators": validator_set.len(),
            "new_records": new_this_tick,
        });
        let line = serde_json::to_string(&summary).expect("serialize summary");
        let _ = writeln!(sum_writer, "{line}");

        total_new += new_this_tick;
        ticks += 1;
        if ticks % FLUSH_EVERY_TICKS == 0 {
            let _ = rec_writer.flush();
            let _ = sum_writer.flush();
        }
        if ticks % 10 == 0 {
            eprintln!(
                "tick {ticks}: peers={} validators={} new={new_this_tick} total_new={total_new}",
                peers.len(),
                validator_set.len()
            );
        }
    }

    exit.store(true, Ordering::Relaxed);
    let _ = gossip_service.join();
    let _ = rec_writer.flush();
    let _ = sum_writer.flush();
    eprintln!(
        "done: {total_new} new records over {ticks} ticks -> {}",
        rec_path.display()
    );
}
