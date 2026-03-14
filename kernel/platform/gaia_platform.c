#include "gaia_platform.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static struct gaia_hw_caps            g_caps;
static struct gaia_device_descriptor  g_devices[GAIA_MAX_DEVICES];
static size_t                         g_device_count;
static int                            g_initialized;

static void gaia_detect_caps(void)
{
    long cpu_count  = sysconf(_SC_NPROCESSORS_ONLN);
    long page_size  = sysconf(_SC_PAGESIZE);
    long page_count = sysconf(_SC_PHYS_PAGES);

    g_caps.logical_cpus = cpu_count > 0 ? (uint32_t)cpu_count : 1;
    g_caps.ram_bytes    = (page_size > 0 && page_count > 0)
        ? (uint64_t)page_size * (uint64_t)page_count
        : 0;

    /* Conservative defaults for a portable reference scaffold. */
    g_caps.has_gpu = false;
    g_caps.has_npu = false;
    g_caps.has_tpm = false;
    g_caps.has_efi = true;
}

int gaia_platform_init(void)
{
    if (g_initialized)
        return 0;

    memset(&g_caps,    0, sizeof(g_caps));
    memset(g_devices,  0, sizeof(g_devices));
    g_device_count = 0;

    gaia_detect_caps();
    g_initialized = 1;
    return 0;
}

int gaia_platform_shutdown(void)
{
    g_initialized  = 0;
    g_device_count = 0;
    memset(&g_caps,   0, sizeof(g_caps));
    memset(g_devices, 0, sizeof(g_devices));
    return 0;
}

int gaia_platform_get_caps(struct gaia_hw_caps *out_caps)
{
    if (!g_initialized || !out_caps)
        return -1;

    *out_caps = g_caps;
    return 0;
}

int gaia_platform_register_device(const struct gaia_device_descriptor *dev)
{
    if (!g_initialized || !dev)
        return -1;
    if (g_device_count >= GAIA_MAX_DEVICES)
        return -1;

    g_devices[g_device_count++] = *dev;
    return 0;
}

int gaia_platform_list_devices(struct gaia_device_descriptor *out, size_t max_items)
{
    if (!g_initialized || !out)
        return -1;

    size_t n = g_device_count < max_items ? g_device_count : max_items;
    for (size_t i = 0; i < n; ++i)
        out[i] = g_devices[i];
    return (int)n;
}

int gaia_platform_classify_workload(const char *process_name, struct gaia_runtime_hint *out_hint)
{
    if (!g_initialized || !process_name || !out_hint)
        return -1;

    memset(out_hint, 0, sizeof(*out_hint));

    if (strncmp(process_name, "gaia-safety", 11) == 0) {
        out_hint->class_id             = GAIA_WL_SAFETY_MONITOR;
        out_hint->latency_budget_us    = 500;
        out_hint->min_slice_us         = 1000;
        out_hint->max_slice_us         = 4000;
        out_hint->isolation_preferred  = true;
        return 0;
    }

    if (strncmp(process_name, "gaia-policy", 11) == 0) {
        out_hint->class_id             = GAIA_WL_POLICY_ENGINE;
        out_hint->latency_budget_us    = 1000;
        out_hint->min_slice_us         = 2000;
        out_hint->max_slice_us         = 6000;
        out_hint->isolation_preferred  = true;
        return 0;
    }

    if (strncmp(process_name, "gaia-core", 9) == 0) {
        out_hint->class_id             = GAIA_WL_CRITICAL_SERVICE;
        out_hint->latency_budget_us    = 2000;
        out_hint->min_slice_us         = 2000;
        out_hint->max_slice_us         = 8000;
        out_hint->isolation_preferred  = false;
        return 0;
    }

    if (strncmp(process_name, "gaia-ui", 7) == 0) {
        out_hint->class_id             = GAIA_WL_INTERACTIVE;
        out_hint->latency_budget_us    = 8000;
        out_hint->min_slice_us         = 1000;
        out_hint->max_slice_us         = 4000;
        out_hint->isolation_preferred  = false;
        return 0;
    }

    out_hint->class_id             = GAIA_WL_BACKGROUND;
    out_hint->latency_budget_us    = 50000;
    out_hint->min_slice_us         = 1000;
    out_hint->max_slice_us         = 2000;
    out_hint->isolation_preferred  = false;
    return 0;
}
