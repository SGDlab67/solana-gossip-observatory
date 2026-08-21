use std::time::Duration;

use anyhow::{anyhow, bail, Context, Result};
use reqwest::blocking::Client;
use serde::Deserialize;
use serde_json::{json, Value};

const RPC_TIMEOUT: Duration = Duration::from_secs(30);

/// Compact getClusterNodes record. Extra RPC fields are ignored.
#[derive(Debug, Clone, Deserialize)]
pub struct ClusterNode {
    pub pubkey: String,
    pub gossip: Option<String>,
    pub rpc: Option<String>,
    pub tpu: Option<String>,
    pub version: Option<String>,
}

/// Compact getVoteAccounts vote-account record. Identity is `nodePubkey`.
#[derive(Debug, Clone, Deserialize)]
pub struct VoteAccount {
    #[serde(rename = "nodePubkey")]
    pub node_pubkey: String,
    #[serde(rename = "activatedStake")]
    pub activated_stake: u64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct VoteAccounts {
    pub current: Vec<VoteAccount>,
    pub delinquent: Vec<VoteAccount>,
}

#[derive(Debug, Deserialize)]
struct JsonRpcError {
    code: i64,
    message: String,
}

#[derive(Debug, Deserialize)]
struct JsonRpcResponse<T> {
    result: Option<T>,
    error: Option<JsonRpcError>,
}

/// Blocking JSON-RPC client for the two public cluster methods we need.
pub struct RpcClient {
    url: String,
    http: Client,
}

impl RpcClient {
    pub fn new(url: impl Into<String>) -> Result<Self> {
        let http = Client::builder()
            .timeout(RPC_TIMEOUT)
            .user_agent("s-nodefinder/0.1")
            .build()
            .context("failed to build HTTP client")?;
        Ok(Self {
            url: url.into(),
            http,
        })
    }

    pub fn get_cluster_nodes(&self) -> Result<Vec<ClusterNode>> {
        self.call("getClusterNodes", json!([]))
    }

    pub fn get_vote_accounts(&self) -> Result<VoteAccounts> {
        self.call("getVoteAccounts", json!([]))
    }

    fn call<T>(&self, method: &str, params: Value) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let body = json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        });

        let response = self
            .http
            .post(&self.url)
            .json(&body)
            .send()
            .with_context(|| format!("RPC request failed ({method} at {})", self.url))?;

        let status = response.status();
        let text = response
            .text()
            .with_context(|| format!("failed to read RPC body ({method})"))?;

        if status.as_u16() == 429 {
            bail!(
                "RPC rate-limited (HTTP 429) for {method} at {}. Wait and retry, or pass --rpc with another endpoint.",
                self.url
            );
        }
        if !status.is_success() {
            bail!(
                "RPC HTTP {status} for {method} at {}: {}",
                self.url,
                truncate_body(&text)
            );
        }

        let parsed: JsonRpcResponse<T> = serde_json::from_str(&text).with_context(|| {
            format!(
                "invalid JSON-RPC response for {method}: {}",
                truncate_body(&text)
            )
        })?;

        if let Some(err) = parsed.error {
            return Err(anyhow!(
                "JSON-RPC error for {method} (code {}): {}",
                err.code,
                err.message
            ));
        }

        parsed
            .result
            .ok_or_else(|| anyhow!("JSON-RPC response for {method} had no result field"))
    }
}

fn truncate_body(text: &str) -> String {
    const MAX: usize = 240;
    let trimmed = text.trim();
    if trimmed.len() <= MAX {
        trimmed.to_string()
    } else {
        format!("{}...", &trimmed[..MAX])
    }
}
