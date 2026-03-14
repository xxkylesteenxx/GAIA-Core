//! Route table — positive-authorization allowlist for IPC dispatch.
//! Spec ref: VIRT-MEM-IPC-SPEC §6
//!
//! A message is dispatched ONLY if an explicit allow entry exists
//! for the (producer, consumer, schema) triple. All other routes
//! are rejected by default.

use crate::endpoint::Endpoint;
use crate::message::{Message, MessageClass};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum RouteError {
    #[error("route not authorized: {0} -> {1} schema={2}")]
    NotAuthorized(String, String, String),

    #[error("high-risk message rejected: missing audit sink")]
    MissingAuditSink,
}

/// A single allow-list entry.
#[derive(Debug, Clone)]
pub struct RouteEntry {
    pub producer: Endpoint,
    pub consumer: Endpoint,
    pub schema:   String,
}

/// Positive-authorization route table.
#[derive(Debug, Default)]
pub struct RouteTable {
    entries:     Vec<RouteEntry>,
    audit_ready: bool,
}

impl RouteTable {
    pub fn new() -> Self { Self::default() }

    pub fn set_audit_ready(&mut self, ready: bool) {
        self.audit_ready = ready;
    }

    pub fn allow(&mut self, entry: RouteEntry) {
        self.entries.push(entry);
    }

    /// Check whether a message is authorized to be dispatched.
    /// Spec ref: §6 — policy check + reject-by-default + audit requirement.
    pub fn check(&self, msg: &Message) -> Result<(), RouteError> {
        if msg.class == MessageClass::HighRisk && !self.audit_ready {
            return Err(RouteError::MissingAuditSink);
        }

        let authorized = self.entries.iter().any(|e| {
            e.producer.name == msg.from
                && e.consumer.name == msg.to
                && e.schema == msg.schema
        });

        if !authorized {
            return Err(RouteError::NotAuthorized(
                msg.from.clone(),
                msg.to.clone(),
                msg.schema.clone(),
            ));
        }

        log::debug!("ipc: authorized {} -> {} [{}]", msg.from, msg.to, msg.schema);
        Ok(())
    }
}
