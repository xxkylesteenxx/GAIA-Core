#ifndef GAIA_BOOT_CONTRACT_H
#define GAIA_BOOT_CONTRACT_H

#include <stdint.h>

#define GAIA_BOOT_MAGIC    0x47414941u /* 'GAIA' */
#define GAIA_MAX_MEM_RANGES 32
#define GAIA_MAX_CMDLINE    256

enum gaia_mem_type {
    GAIA_MEM_RESERVED = 0,
    GAIA_MEM_USABLE   = 1,
    GAIA_MEM_ACPI     = 2,
    GAIA_MEM_MMIO     = 3,
};

struct gaia_mem_range {
    uint64_t base;
    uint64_t length;
    uint32_t type;
    uint32_t flags;
};

struct gaia_hw_identity {
    uint32_t cpu_vendor;
    uint32_t cpu_family;
    uint32_t cpu_model;
    uint32_t cpu_stepping;
    uint64_t features_lo;
    uint64_t features_hi;
    uint8_t  has_tpm;
    uint8_t  has_efi;
    uint8_t  has_acpi;
    uint8_t  reserved0;
};

struct gaia_framebuffer_info {
    uint64_t base;
    uint32_t width;
    uint32_t height;
    uint32_t pitch;
    uint32_t bpp;
};

struct gaia_boot_contract {
    uint32_t magic;
    uint16_t version_major;
    uint16_t version_minor;
    uint64_t boot_flags;

    struct gaia_hw_identity      hw;
    struct gaia_framebuffer_info fb;

    uint32_t               mem_range_count;
    struct gaia_mem_range  mem_ranges[GAIA_MAX_MEM_RANGES];

    char cmdline[GAIA_MAX_CMDLINE];
};

#endif /* GAIA_BOOT_CONTRACT_H */
