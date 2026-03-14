//! GAIA IPC message envelope v2 — typed, signed, policy-authorized.
//!
//! Spec ref: VIRT-MEM-IPC-SPEC §6
//!
//! This module supersedes the `message.rs` stub with a concrete
//! signed envelope, a topic-prefix route policy, and sign/verify
//! helpers backed by SHA-256.
//!
//! # Auth model
//!
//! `sign_message` and `verify_message` implement a symmetric
//! HMAC-style construction over a shared secret:
//!
//!   auth_tag = SHA-256(secret || from || to || topic || nonce_le || payload)
//!
//! The nonce field MUST be monotonically increasing per (from, to) pair
//! to prevent replay attacks. Nonce management is the caller's responsibility.

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use thiserror::Error;

// ── Message envelope ─────────────────────────────────────────────────────────────

/// A typed, signed IPC message envelope.
///
/// Fields are bound into the `auth_tag` digest; mutating any field
/// after signing invalidates the tag.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GaiaMessage {
    /// Sender domain/endpoint name.
    pub from:     String,
    /// Receiver domain/endpoint name.
    pub to:       String,
    /// Hierarchical topic string, e.g. `"gaia.safety.alert/v1"`.
    pub topic:    String,
    /// Per-(from,to) monotonic counter; prevents replay.
    pub nonce:    u64,
    /// Opaque payload bytes (serialized schema body).
    pub payload:  Vec<u8>,
    /// SHA-256 auth tag over (secret || from || to || topic || nonce_le || payload).
    pub auth_tag: Vec<u8>,
}

// ── Route policy ────────────────────────────────────────────────────────────────

/// A single positive-authorization route rule.
///
/// A message is allowed if all three fields match:
///   - `from` equals `msg.from`
///   - `to`   equals `msg.to`
///   - `msg.topic` starts with `topic_prefix`
///
/// Spec ref: VIRT-MEM-IPC-SPEC §6 — explicit allowlists, reject-by-default.
#[derive(Debug, Clone)]
pub struct RoutePolicy {
    pub from:         String,
    pub to:           String,
    pub topic_prefix: String,
}

// ── Errors ────────────────────────────────────────────────────────────────────────

#[derive(Debug, Error)]
pub enum IpcError {
    #[error("route denied: {from} -> {to} topic={topic}")]
    RouteDenied {
        from:  String,
        to:    String,
        topic: String,
    },
    #[error("authentication tag mismatch")]
    AuthFailed,
}

// ── Functions ─────────────────────────────────────────────────────────────────────

/// Check whether `msg` is authorized under `rules`.
///
/// Returns `Ok(())` if any rule matches; `Err(IpcError::RouteDenied)` otherwise.
/// Spec ref: VIRT-MEM-IPC-SPEC §6 — policy check before dispatch.
pub fn authorize(msg: &GaiaMessage, rules: &[RoutePolicy]) -> Result<(), IpcError> {
    let allowed = rules.iter().any(|r| {
        r.from == msg.from
            && r.to == msg.to
            && msg.topic.starts_with(&r.topic_prefix)
    });

    if allowed {
        Ok(())
    } else {
        Err(IpcError::RouteDenied {
            from:  msg.from.clone(),
            to:    msg.to.clone(),
            topic: msg.topic.clone(),
        })
    }
}

/// Sign `msg` by computing its auth_tag in-place and returning the updated envelope.
///
/// auth_tag = SHA-256(secret || from || to || topic || nonce_le64 || payload)
///
/// The `secret` is a shared symmetric key; use a per-(from,to) derived key
/// in production to prevent cross-endpoint forgery.
pub fn sign_message(secret: &[u8], mut msg: GaiaMessage) -> GaiaMessage {
    msg.auth_tag = compute_tag(secret, &msg);
    msg
}

/// Verify `msg.auth_tag` against a freshly computed tag.
///
/// Returns `Ok(())` on match, `Err(IpcError::AuthFailed)` on mismatch.
/// Does NOT validate the nonce — replay detection is the caller's responsibility.
pub fn verify_message(secret: &[u8], msg: &GaiaMessage) -> Result<(), IpcError> {
    let expected = compute_tag(secret, msg);
    // Constant-time comparison to resist timing side-channels.
    if constant_time_eq(&expected, &msg.auth_tag) {
        Ok(())
    } else {
        Err(IpcError::AuthFailed)
    }
}

// ── Internal helpers ──────────────────────────────────────────────────────────────

fn compute_tag(secret: &[u8], msg: &GaiaMessage) -> Vec<u8> {
    let mut h = Sha256::new();
    h.update(secret);
    h.update(msg.from.as_bytes());
    h.update(msg.to.as_bytes());
    h.update(msg.topic.as_bytes());
    h.update(msg.nonce.to_le_bytes());
    h.update(&msg.payload);
    h.finalize().to_vec()
}

/// Naive constant-time byte-slice equality.
/// For production, replace with `subtle::ConstantTimeEq`.
fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    a.iter().zip(b.iter()).fold(0u8, |acc, (x, y)| acc | (x ^ y)) == 0
}

// ── Tests ──────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn make_msg() -> GaiaMessage {
        GaiaMessage {
            from:     "terra".into(),
            to:       "sophia".into(),
            topic:    "gaia.event.state/v1".into(),
            nonce:    1,
            payload:  b"hello".to_vec(),
            auth_tag: Vec::new(),
        }
    }

    #[test]
    fn sign_and_verify_ok() {
        let secret = b"test-secret";
        let signed = sign_message(secret, make_msg());
        assert!(verify_message(secret, &signed).is_ok());
    }

    #[test]
    fn wrong_secret_fails() {
        let signed = sign_message(b"correct", make_msg());
        assert!(verify_message(b"wrong", &signed).is_err());
    }

    #[test]
    fn tampered_payload_fails() {
        let secret = b"test-secret";
        let mut signed = sign_message(secret, make_msg());
        signed.payload.push(0xff);
        assert!(verify_message(secret, &signed).is_err());
    }

    #[test]
    fn route_allow() {
        let rules = vec![RoutePolicy {
            from:         "terra".into(),
            to:           "sophia".into(),
            topic_prefix: "gaia.event.".into(),
        }];
        let msg = make_msg();
        assert!(authorize(&msg, &rules).is_ok());
    }

    #[test]
    fn route_deny_unknown_sender() {
        let rules = vec![RoutePolicy {
            from:         "guardian".into(),
            to:           "sophia".into(),
            topic_prefix: "gaia.".into(),
        }];
        let msg = make_msg(); // from=terra, not guardian
        assert!(matches!(authorize(&msg, &rules), Err(IpcError::RouteDenied { .. })));
    }
}
