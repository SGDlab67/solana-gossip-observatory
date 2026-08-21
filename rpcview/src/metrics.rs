use std::collections::{HashMap, HashSet};

use serde::Serialize;

use crate::rpc::{ClusterNode, VoteAccount};
use crate::snapshot::host_from_socket;

const TOP_VERSIONS: usize = 8;

#[derive(Debug, Clone, Serialize)]
pub struct VersionCount {
    pub version: String,
    pub count: usize,
}

/// Degree-of-anonymity summary numbers for one snapshot.
#[derive(Debug, Clone, Serialize)]
pub struct Summary {
    pub captured_at: String,
    pub cluster_node_count: usize,
    pub unique_gossip_ips: usize,
    pub rpc_endpoint_count: usize,
    pub current_validators: usize,
    pub delinquent_validators: usize,
    pub current_validators_with_gossip_ip: usize,
    /// Fraction of current activated stake whose identity appears in getClusterNodes with a gossip address.
    pub stake_weighted_identified_fraction: f64,
    pub top_versions: Vec<VersionCount>,
}

/// Identity pubkeys from cluster nodes that advertise a gossip address.
pub fn identities_with_gossip(nodes: &[ClusterNode]) -> HashSet<String> {
    nodes
        .iter()
        .filter(|n| n.gossip.as_deref().is_some_and(|g| !g.is_empty()))
        .map(|n| n.pubkey.clone())
        .collect()
}

pub fn compute_summary(
    captured_at: impl Into<String>,
    nodes: &[ClusterNode],
    current: &[VoteAccount],
    delinquent: &[VoteAccount],
) -> Summary {
    let gossip_identities = identities_with_gossip(nodes);

    let unique_gossip_ips: HashSet<String> = nodes
        .iter()
        .filter_map(|n| n.gossip.as_deref())
        .filter_map(host_from_socket)
        .collect();

    let rpc_endpoint_count = nodes
        .iter()
        .filter(|n| n.rpc.as_deref().is_some_and(|rpc| !rpc.is_empty()))
        .count();

    let current_validators_with_gossip_ip = current
        .iter()
        .filter(|v| gossip_identities.contains(&v.node_pubkey))
        .count();

    let total_stake: u128 = current.iter().map(|v| u128::from(v.activated_stake)).sum();
    let identified_stake: u128 = current
        .iter()
        .filter(|v| gossip_identities.contains(&v.node_pubkey))
        .map(|v| u128::from(v.activated_stake))
        .sum();
    let stake_weighted_identified_fraction = if total_stake == 0 {
        0.0
    } else {
        identified_stake as f64 / total_stake as f64
    };

    Summary {
        captured_at: captured_at.into(),
        cluster_node_count: nodes.len(),
        unique_gossip_ips: unique_gossip_ips.len(),
        rpc_endpoint_count,
        current_validators: current.len(),
        delinquent_validators: delinquent.len(),
        current_validators_with_gossip_ip,
        stake_weighted_identified_fraction,
        top_versions: version_histogram(nodes),
    }
}

fn version_histogram(nodes: &[ClusterNode]) -> Vec<VersionCount> {
    let mut counts: HashMap<String, usize> = HashMap::new();
    for node in nodes {
        let label = match node.version.as_deref() {
            Some(v) if !v.is_empty() => v.to_string(),
            _ => "unknown".to_string(),
        };
        *counts.entry(label).or_insert(0) += 1;
    }
    let mut entries: Vec<VersionCount> = counts
        .into_iter()
        .map(|(version, count)| VersionCount { version, count })
        .collect();
    entries.sort_by(|a, b| {
        b.count
            .cmp(&a.count)
            .then_with(|| a.version.cmp(&b.version))
    });
    entries.truncate(TOP_VERSIONS);
    entries
}

pub fn print_summary(rpc_url: &str, summary: &Summary) {
    println!("S-NodeFinder snapshot");
    println!("timestamp:                         {}", summary.captured_at);
    println!("rpc:                               {rpc_url}");
    println!(
        "cluster nodes:                     {}",
        summary.cluster_node_count
    );
    println!(
        "unique gossip IPs:                 {}",
        summary.unique_gossip_ips
    );
    println!(
        "exposing an RPC endpoint:          {}",
        summary.rpc_endpoint_count
    );
    println!(
        "current validators:                {}",
        summary.current_validators
    );
    println!(
        "delinquent validators:             {}",
        summary.delinquent_validators
    );
    println!(
        "overlap (current with gossip IP):  {}",
        summary.current_validators_with_gossip_ip
    );
    println!(
        "stake-weighted identified:         {:.2}% of current activated stake",
        summary.stake_weighted_identified_fraction * 100.0
    );
    println!("top versions:");
    if summary.top_versions.is_empty() {
        println!("  (none)");
    } else {
        for entry in &summary.top_versions {
            println!("  {:<24} {:>8}", entry.version, entry.count);
        }
    }
    println!();
    println!("Note: counts churn live. Treat this as a point-in-time sample.");
    println!("Note: stake-weighted identified is this RPC's view of gossip ContactInfo,");
    println!("      not a newly discovered mapping. Compare later spy crawls to this baseline.");
}

#[cfg(test)]
mod tests {
    use super::*;

    fn node(
        pubkey: &str,
        gossip: Option<&str>,
        rpc: Option<&str>,
        version: Option<&str>,
    ) -> ClusterNode {
        ClusterNode {
            pubkey: pubkey.to_string(),
            gossip: gossip.map(str::to_string),
            rpc: rpc.map(str::to_string),
            tpu: None,
            version: version.map(str::to_string),
        }
    }

    fn vote(pubkey: &str, stake: u64) -> VoteAccount {
        VoteAccount {
            node_pubkey: pubkey.to_string(),
            activated_stake: stake,
        }
    }

    #[test]
    fn stake_weighted_fraction_and_overlap() {
        let nodes = vec![
            node(
                "A",
                Some("1.1.1.1:8001"),
                Some("1.1.1.1:8899"),
                Some("2.1.0"),
            ),
            node("B", Some("2.2.2.2:8001"), None, Some("2.1.0")),
            node("C", None, None, Some("2.0.0")),
            node("D", Some("1.1.1.1:8001"), None, Some("2.0.0")),
        ];
        let current = vec![vote("A", 70), vote("C", 30), vote("Z", 0)];
        let delinquent = vec![vote("B", 5)];
        let summary = compute_summary("t", &nodes, &current, &delinquent);

        assert_eq!(summary.cluster_node_count, 4);
        assert_eq!(summary.unique_gossip_ips, 2);
        assert_eq!(summary.rpc_endpoint_count, 1);
        assert_eq!(summary.current_validators, 3);
        assert_eq!(summary.delinquent_validators, 1);
        assert_eq!(summary.current_validators_with_gossip_ip, 1);
        assert!((summary.stake_weighted_identified_fraction - 0.70).abs() < 1e-9);
        assert_eq!(summary.top_versions.len(), 2);
        assert_eq!(summary.top_versions[0].count, 2);
        assert_eq!(summary.top_versions[1].count, 2);
        let versions: Vec<&str> = summary
            .top_versions
            .iter()
            .map(|v| v.version.as_str())
            .collect();
        assert!(versions.contains(&"2.1.0"));
        assert!(versions.contains(&"2.0.0"));
    }
}
