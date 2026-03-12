// GAIA L0 Early Init — C
// Layer: L0 (Boot / Hardware Entry)
// Handles: UEFI handoff, TPM setup, CPU topology detection, memory map parsing
// See: docs/specs/platform/GAIALanguageStackSpecv1.0.md

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/efi.h>

/**
 * gaia_early_init - GAIA early boot initialization
 * Called from x86_64.S boot stub after stack setup.
 * Performs: UEFI/EFI handoff, TPM measurement, memory map, CPU init.
 */
void __init gaia_early_init(void)
{
    /* 1. Parse EFI/UEFI memory map */
    // efi_init() called by Linux before this point in real kernel

    /* 2. Establish TPM measured boot chain */
    // tpm_early_init() — placeholder for GAIA boot attestation

    /* 3. Detect CPU topology for consciousness core assignment */
    // gaia_cpu_topology_init() — map physical CPUs to CCO/ICO/ACO/BCO domains

    /* 4. Hand off to Rust kernel init */
    // gaia_kernel_init() — defined in kernel/src/lib.rs
    extern int gaia_kernel_init(void);
    int ret = gaia_kernel_init();
    if (ret != 0) {
        panic("GAIA: Rust kernel init failed: %d\n", ret);
    }
}
