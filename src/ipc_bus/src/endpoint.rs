//! IPC endpoint — named, authenticated identity on the bus.
//! Spec ref: VIRT-MEM-IPC-SPEC §6

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Endpoint {
    pub name:   String,
    pub domain: String,
}

impl Endpoint {
    pub fn new(name: impl Into<String>, domain: impl Into<String>) -> Self {
        Self { name: name.into(), domain: domain.into() }
    }
}
