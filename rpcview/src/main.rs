mod metrics;
mod rpc;
mod snapshot;

use std::path::PathBuf;

use anyhow::{Context, Result};
use chrono::{SecondsFormat, Utc};
use clap::{Parser, Subcommand};

use crate::metrics::print_summary;
use crate::rpc::RpcClient;
use crate::snapshot::Snapshot;

const DEFAULT_RPC: &str = "https://api.mainnet-beta.solana.com";
const DEFAULT_OUT: &str = "snapshots/latest.json";

#[derive(Parser)]
#[command(
    name = "s-nodefinder",
    about = "Read-only Solana cluster snapshot tool. Measures how readily validator identities map to gossip IPs.",
    version
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Capture getClusterNodes + getVoteAccounts and write a JSON snapshot.
    Snapshot {
        /// Solana JSON-RPC URL (read-only).
        #[arg(long, default_value = DEFAULT_RPC)]
        rpc: String,
        /// Output snapshot path.
        #[arg(long, default_value = DEFAULT_OUT)]
        out: PathBuf,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Command::Snapshot { rpc, out } => run_snapshot(rpc, out),
    }
}

fn run_snapshot(rpc_url: String, out: PathBuf) -> Result<()> {
    let client = RpcClient::new(&rpc_url)?;
    let captured_at = Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true);

    let nodes = client
        .get_cluster_nodes()
        .context("getClusterNodes failed")?;
    let votes = client
        .get_vote_accounts()
        .context("getVoteAccounts failed")?;

    let snapshot = Snapshot::from_rpc(captured_at, rpc_url.clone(), &nodes, &votes);
    snapshot.write_json(&out)?;
    print_summary(&rpc_url, &snapshot.summary);
    println!("wrote {}", out.display());
    Ok(())
}
