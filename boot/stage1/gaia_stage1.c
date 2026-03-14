/*
 * gaia_stage1.c
 * Minimal early bring-up scaffold.
 * This file is deliberately tiny and conservative: initialize a boot contract,
 * perform placeholder platform discovery, and hand off to a future kernel entry.
 */

#include <stdint.h>
#include "gaia_boot_contract.h"

static struct gaia_boot_contract g_contract;

static void gaia_boot_contract_init(struct gaia_boot_contract *c)
{
    c->magic         = GAIA_BOOT_MAGIC;
    c->version_major = 1;
    c->version_minor = 0;
    c->boot_flags    = 0;

    c->hw.cpu_vendor   = 0;
    c->hw.cpu_family   = 0;
    c->hw.cpu_model    = 0;
    c->hw.cpu_stepping = 0;
    c->hw.features_lo  = 0;
    c->hw.features_hi  = 0;
    c->hw.has_tpm      = 0;
    c->hw.has_efi      = 0;
    c->hw.has_acpi     = 0;

    c->fb.base   = 0;
    c->fb.width  = 0;
    c->fb.height = 0;
    c->fb.pitch  = 0;
    c->fb.bpp    = 0;

    c->mem_range_count = 0;
    for (int i = 0; i < GAIA_MAX_MEM_RANGES; ++i) {
        c->mem_ranges[i].base   = 0;
        c->mem_ranges[i].length = 0;
        c->mem_ranges[i].type   = GAIA_MEM_RESERVED;
        c->mem_ranges[i].flags  = 0;
    }

    for (int i = 0; i < GAIA_MAX_CMDLINE; ++i)
        c->cmdline[i] = '\0';
}

static void gaia_platform_probe_stub(struct gaia_boot_contract *c)
{
    /* Placeholder values for research bring-up. */
    c->hw.has_efi  = 1;
    c->hw.has_acpi = 1;
    c->mem_range_count          = 1;
    c->mem_ranges[0].base       = 0x00100000ULL;
    c->mem_ranges[0].length     = 0x1FF00000ULL;
    c->mem_ranges[0].type       = GAIA_MEM_USABLE;
}

static void gaia_kernel_handoff(const struct gaia_boot_contract *c)
{
    (void)c;
    /* Future: jump to decompressor, EFI stub entry, or custom kernel entry. */
    for (;;) {
        __asm__ volatile("hlt");
    }
}

void gaia_stage1_main(void)
{
    gaia_boot_contract_init(&g_contract);
    gaia_platform_probe_stub(&g_contract);
    gaia_kernel_handoff(&g_contract);
}
