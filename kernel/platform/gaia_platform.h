#ifndef GAIA_PLATFORM_H
#define GAIA_PLATFORM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define GAIA_MAX_DEVICES 64
#define GAIA_NAME_LEN    64

enum gaia_device_class {
    GAIA_DEV_CPU = 0,
    GAIA_DEV_MEMORY,
    GAIA_DEV_STORAGE,
    GAIA_DEV_NETWORK,
    GAIA_DEV_SENSOR,
    GAIA_DEV_ACCELERATOR,
};

enum gaia_workload_class {
    GAIA_WL_BACKGROUND = 0,
    GAIA_WL_INTERACTIVE,
    GAIA_WL_CRITICAL_SERVICE,
    GAIA_WL_POLICY_ENGINE,
    GAIA_WL_SAFETY_MONITOR,
};

struct gaia_hw_caps {
    uint32_t logical_cpus;
    uint64_t ram_bytes;
    bool     has_gpu;
    bool     has_npu;
    bool     has_tpm;
    bool     has_efi;
};

struct gaia_device_descriptor {
    enum gaia_device_class class_id;
    uint32_t               instance;
    uint64_t               flags;
    char                   name[GAIA_NAME_LEN];
};

struct gaia_runtime_hint {
    enum gaia_workload_class class_id;
    uint32_t                 latency_budget_us;
    uint32_t                 min_slice_us;
    uint32_t                 max_slice_us;
    bool                     isolation_preferred;
};

int gaia_platform_init(void);
int gaia_platform_shutdown(void);
int gaia_platform_get_caps(struct gaia_hw_caps *out_caps);
int gaia_platform_register_device(const struct gaia_device_descriptor *dev);
int gaia_platform_list_devices(struct gaia_device_descriptor *out, size_t max_items);
int gaia_platform_classify_workload(const char *process_name, struct gaia_runtime_hint *out_hint);

#endif /* GAIA_PLATFORM_H */
