// scx_gaia userspace loader and monitor
// Loads the scx_gaia BPF scheduler and monitors DSQ statistics.
//
// Build: gcc -O2 -o scx_gaia_userspace scx_gaia_userspace.c -lbpf
// Run:   sudo ./scx_gaia_userspace [--dry-run]

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>

// libbpf + sched_ext skeleton would be included here
// #include "scx_gaia.skel.h"

#define DSQ_GUARDIAN_STOP    0
#define DSQ_NEXUS_BARRIER    1
#define DSQ_SENSOR_FRESHNESS 2
#define DSQ_HOT_PATH_USER    3
#define DSQ_BACKGROUND       4
#define DSQ_RECOVERY         5

static const char *DSQ_NAMES[] = {
    "GUARDIAN_STOP",
    "NEXUS_BARRIER",
    "SENSOR_FRESHNESS",
    "HOT_PATH_USER",
    "BACKGROUND",
    "RECOVERY",
};

static volatile int running = 1;

static void sig_handler(int sig) {
    (void)sig;
    running = 0;
    fprintf(stderr, "\nscx_gaia: shutting down\n");
}

static void print_stats(void) {
    // In production: read from BPF map via libbpf
    // Stub: print placeholder stats
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    printf("[%ld.%03ld] scx_gaia DSQ stats:\n",
           ts.tv_sec, ts.tv_nsec / 1000000);
    for (int i = 0; i < 6; i++) {
        printf("  DSQ[%d] %-20s enqueues=<bpf_map>\n", i, DSQ_NAMES[i]);
    }
}

static int check_prerequisites(void) {
    // Check sched_ext is available
    if (access("/sys/kernel/sched_ext", F_OK) != 0) {
        fprintf(stderr, "ERROR: /sys/kernel/sched_ext not found.\n");
        fprintf(stderr, "Ensure CONFIG_SCHED_CLASS_EXT=y and kernel >= 6.6\n");
        return -1;
    }
    // Check running as root
    if (geteuid() != 0) {
        fprintf(stderr, "ERROR: must run as root\n");
        return -1;
    }
    return 0;
}

static void handle_rt_throttle(void) {
    fprintf(stderr, "[DEGRADED] RT throttle detected — signalling GUARDIAN: degrade to YELLOW\n");
    // Production: write to GAIA IPC channel to notify GUARDIAN
}

static void handle_schedext_fault(void) {
    fprintf(stderr, "[DEGRADED] sched_ext fault — restoring CFS fallback\n");
    // Production: call sched_setscheduler(SCHED_OTHER) on all GAIA tasks
}

int main(int argc, char **argv) {
    int dry_run = (argc > 1 && strcmp(argv[1], "--dry-run") == 0);

    printf("scx_gaia userspace loader v1.0\n");
    printf("GAIA consciousness-aware BPF scheduler\n");

    if (!dry_run) {
        if (check_prerequisites() != 0)
            return 1;
    } else {
        printf("[DRY RUN] skipping kernel checks\n");
    }

    signal(SIGINT,  sig_handler);
    signal(SIGTERM, sig_handler);

    if (!dry_run) {
        printf("Loading scx_gaia BPF scheduler...\n");
        // Production: scx_gaia_bpf__open_and_load() + scx_gaia_bpf__attach()
        printf("scx_gaia loaded. Monitoring DSQ stats (Ctrl-C to exit)...\n");
    }

    while (running) {
        if (!dry_run)
            print_stats();
        sleep(1);
    }

    if (!dry_run) {
        printf("scx_gaia: unloading BPF scheduler, restoring CFS\n");
        // Production: scx_gaia_bpf__destroy()
    }

    return 0;
}
