use std::fs;
use std::path::Path;

use anyhow::{Context, Result};
use serde::Serialize;

use crate::metrics::{compute_summary, Summary};
use crate::rpc::{ClusterNode, VoteAccounts};

/// Compact cluster-node record written to the snapshot file.
#[derive(Debug, Clone, Serialize)]
pub struct SnapshotNode {
    pub pubkey: String,
    pub gossip: Option<String>,
    pub rpc: Option<String>,
    pub tpu: Option<String>,
    pub version: Option<String>,
}

/// Compact validator record. `pubkey` is the identity (node) pubkey.
#[derive(Debug, Clone, Serialize)]
pub struct SnapshotValidator {
    pub pubkey: String,
    pub activated_stake: u64,
    pub delinquent: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct Snapshot {
    pub captured_at: String,
    pub rpc_url: String,
    pub summary: Summary,
    pub nodes: Vec<SnapshotNode>,
    pub validators: Vec<SnapshotValidator>,
}

impl Snapshot {
    /// Join getClusterNodes with getVoteAccounts on identity/node pubkey.
    pub fn from_rpc(
        captured_at: String,
        rpc_url: String,
        nodes: &[ClusterNode],
        votes: &VoteAccounts,
    ) -> Self {
        let summary = compute_summary(&captured_at, nodes, &votes.current, &votes.delinquent);
        let snapshot_nodes = nodes
            .iter()
            .map(|n| SnapshotNode {
                pubkey: n.pubkey.clone(),
                gossip: n.gossip.clone(),
                rpc: n.rpc.clone(),
                tpu: n.tpu.clone(),
                version: n.version.clone(),
            })
            .collect();
        let mut validators = Vec::with_capacity(votes.current.len() + votes.delinquent.len());
        validators.extend(votes.current.iter().map(|v| SnapshotValidator {
            pubkey: v.node_pubkey.clone(),
            activated_stake: v.activated_stake,
            delinquent: false,
        }));
        validators.extend(votes.delinquent.iter().map(|v| SnapshotValidator {
            pubkey: v.node_pubkey.clone(),
            activated_stake: v.activated_stake,
            delinquent: true,
        }));

        Self {
            captured_at,
            rpc_url,
            summary,
            nodes: snapshot_nodes,
            validators,
        }
    }

    pub fn write_json(&self, path: &Path) -> Result<()> {
        if let Some(parent) = path.parent() {
            if !parent.as_os_str().is_empty() {
                fs::create_dir_all(parent)
                    .with_context(|| format!("failed to create {}", parent.display()))?;
            }
        }
        let json = serde_json::to_string_pretty(self).context("failed to serialize snapshot")?;
        fs::write(path, json).with_context(|| format!("failed to write {}", path.display()))?;
        Ok(())
    }
}

/// Extract the host/IP from a `host:port` or `[ipv6]:port` gossip/RPC socket string.
pub fn host_from_socket(addr: &str) -> Option<String> {
    let addr = addr.trim();
    if addr.is_empty() {
        return None;
    }
    if let Some(rest) = addr.strip_prefix('[') {
        let host = rest.split(']').next().unwrap_or("");
        if host.is_empty() {
            return None;
        }
        return Some(host.to_string());
    }
    let host = addr.rsplit_once(':').map(|(h, _)| h).unwrap_or(addr);
    if host.is_empty() {
        None
    } else {
        Some(host.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::host_from_socket;

    #[test]
    fn parses_ipv4_and_ipv6_sockets() {
        assert_eq!(
            host_from_socket("10.239.6.48:8001").as_deref(),
            Some("10.239.6.48")
        );
        assert_eq!(
            host_from_socket("[2001:db8::1]:8001").as_deref(),
            Some("2001:db8::1")
        );
        assert_eq!(host_from_socket(""), None);
    }
}
