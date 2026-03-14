//! Message types for the GAIA IPC bus.
//! Spec ref: VIRT-MEM-IPC-SPEC §6

/// Priority / risk class for a message.
/// High-risk classes trigger durability and audit requirements.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MessageClass {
    /// Routine informational exchange.
    Telemetry,
    /// Coordinated state change request.
    Control,
    /// Safety-critical or policy-enforcement command.
    HighRisk,
}

/// A typed, versioned IPC message.
#[derive(Debug, Clone)]
pub struct Message {
    pub from:    String,
    pub to:      String,
    pub class:   MessageClass,
    pub schema:  String,   // e.g. "gaia.sched.classify/v1"
    pub payload: Vec<u8>,
}
