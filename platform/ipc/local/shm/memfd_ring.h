#ifndef GAIA_MEMFD_RING_H
#define GAIA_MEMFD_RING_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define GAIA_MEMFD_RING_MAGIC 0x4741494152494E47ULL /* "GAIARING" */
#define GAIA_MEMFD_RING_VERSION 1U

struct gaia_memfd_ring_meta {
    uint64_t magic;
    uint32_t version;
    uint32_t flags;
    uint32_t slot_count;
    uint32_t slot_size;
    volatile uint64_t head;
    volatile uint64_t tail;
    volatile uint64_t dropped;
    volatile uint64_t overruns;
    char reserved[64 - 8 - 4 - 4 - 4 - 4 - 8 - 8 - 8 - 8];
};

struct gaia_memfd_ring {
    int fd;
    size_t map_len;
    uint8_t *mapping;
    struct gaia_memfd_ring_meta *meta;
    uint8_t *slots;
};

struct gaia_memfd_ring_slot_view {
    void *ptr;
    uint64_t seq;
    uint32_t len;
};

int gaia_memfd_ring_create(struct gaia_memfd_ring *ring,
                           const char *name,
                           uint32_t slot_count,
                           uint32_t slot_size,
                           bool seal_after_init);

int gaia_memfd_ring_attach(struct gaia_memfd_ring *ring,
                           int fd,
                           size_t expected_map_len);

void gaia_memfd_ring_close(struct gaia_memfd_ring *ring);
size_t gaia_memfd_ring_required_len(uint32_t slot_count, uint32_t slot_size);

int gaia_memfd_ring_begin_write(struct gaia_memfd_ring *ring,
                                struct gaia_memfd_ring_slot_view *view);
int gaia_memfd_ring_commit_write(struct gaia_memfd_ring *ring,
                                 const struct gaia_memfd_ring_slot_view *view,
                                 uint32_t len);
int gaia_memfd_ring_abort_write(struct gaia_memfd_ring *ring,
                                const struct gaia_memfd_ring_slot_view *view);

int gaia_memfd_ring_begin_read(struct gaia_memfd_ring *ring,
                               struct gaia_memfd_ring_slot_view *view);
int gaia_memfd_ring_commit_read(struct gaia_memfd_ring *ring,
                                const struct gaia_memfd_ring_slot_view *view);

bool gaia_memfd_ring_empty(const struct gaia_memfd_ring *ring);
bool gaia_memfd_ring_full(const struct gaia_memfd_ring *ring);

#ifdef __cplusplus
}
#endif

#endif /* GAIA_MEMFD_RING_H */
