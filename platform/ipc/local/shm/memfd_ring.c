#define _GNU_SOURCE
#include "memfd_ring.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/memfd.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>

#ifndef MFD_CLOEXEC
#define MFD_CLOEXEC 0x0001U
#endif

#ifndef MFD_ALLOW_SEALING
#define MFD_ALLOW_SEALING 0x0002U
#endif

static int gaia_memfd_create(const char *name, unsigned int flags) {
    return (int)syscall(SYS_memfd_create, name, flags);
}

size_t gaia_memfd_ring_required_len(uint32_t slot_count, uint32_t slot_size) {
    return sizeof(struct gaia_memfd_ring_meta) + ((size_t)slot_count * (size_t)slot_size);
}

static void *gaia_mmap_shared(int fd, size_t len) {
    return mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
}

static bool gaia_slot_index_valid(const struct gaia_memfd_ring *ring, uint64_t seq) {
    return ring && ring->meta && ring->meta->slot_count > 0 && seq >= ring->meta->tail;
}

int gaia_memfd_ring_create(struct gaia_memfd_ring *ring,
                           const char *name,
                           uint32_t slot_count,
                           uint32_t slot_size,
                           bool seal_after_init) {
    if (!ring || !name || slot_count == 0 || slot_size == 0) {
        return EINVAL;
    }

    memset(ring, 0, sizeof(*ring));

    const unsigned int flags = MFD_CLOEXEC | MFD_ALLOW_SEALING;
    const int fd = gaia_memfd_create(name, flags);
    if (fd < 0) {
        return errno;
    }

    const size_t len = gaia_memfd_ring_required_len(slot_count, slot_size);
    if (ftruncate(fd, (off_t)len) != 0) {
        const int saved = errno;
        close(fd);
        return saved;
    }

    void *mapping = gaia_mmap_shared(fd, len);
    if (mapping == MAP_FAILED) {
        const int saved = errno;
        close(fd);
        return saved;
    }

    ring->fd = fd;
    ring->map_len = len;
    ring->mapping = (uint8_t *)mapping;
    ring->meta = (struct gaia_memfd_ring_meta *)mapping;
    ring->slots = ring->mapping + sizeof(struct gaia_memfd_ring_meta);

    memset(ring->mapping, 0, len);
    ring->meta->magic = GAIA_MEMFD_RING_MAGIC;
    ring->meta->version = GAIA_MEMFD_RING_VERSION;
    ring->meta->slot_count = slot_count;
    ring->meta->slot_size = slot_size;

    if (seal_after_init) {
        if (fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL) != 0) {
            gaia_memfd_ring_close(ring);
            return errno;
        }
    }

    return 0;
}

int gaia_memfd_ring_attach(struct gaia_memfd_ring *ring, int fd, size_t expected_map_len) {
    if (!ring || fd < 0) {
        return EINVAL;
    }

    memset(ring, 0, sizeof(*ring));

    struct stat st;
    if (fstat(fd, &st) != 0) {
        return errno;
    }

    size_t len = (size_t)st.st_size;
    if (expected_map_len > 0 && expected_map_len != len) {
        return EINVAL;
    }

    void *mapping = gaia_mmap_shared(fd, len);
    if (mapping == MAP_FAILED) {
        return errno;
    }

    ring->fd = fd;
    ring->map_len = len;
    ring->mapping = (uint8_t *)mapping;
    ring->meta = (struct gaia_memfd_ring_meta *)mapping;
    ring->slots = ring->mapping + sizeof(struct gaia_memfd_ring_meta);

    if (ring->meta->magic != GAIA_MEMFD_RING_MAGIC || ring->meta->version != GAIA_MEMFD_RING_VERSION) {
        gaia_memfd_ring_close(ring);
        return EPROTO;
    }
    return 0;
}

void gaia_memfd_ring_close(struct gaia_memfd_ring *ring) {
    if (!ring) {
        return;
    }
    if (ring->mapping && ring->mapping != MAP_FAILED) {
        munmap(ring->mapping, ring->map_len);
    }
    if (ring->fd > 0) {
        close(ring->fd);
    }
    memset(ring, 0, sizeof(*ring));
}

bool gaia_memfd_ring_empty(const struct gaia_memfd_ring *ring) {
    return !ring || !ring->meta || atomic_load((_Atomic uint64_t *)&ring->meta->head) ==
           atomic_load((_Atomic uint64_t *)&ring->meta->tail);
}

bool gaia_memfd_ring_full(const struct gaia_memfd_ring *ring) {
    if (!ring || !ring->meta) {
        return false;
    }
    const uint64_t head = atomic_load((_Atomic uint64_t *)&ring->meta->head);
    const uint64_t tail = atomic_load((_Atomic uint64_t *)&ring->meta->tail);
    return (head - tail) >= ring->meta->slot_count;
}

int gaia_memfd_ring_begin_write(struct gaia_memfd_ring *ring,
                                struct gaia_memfd_ring_slot_view *view) {
    if (!ring || !ring->meta || !view) {
        return EINVAL;
    }

    const uint64_t head = atomic_load((_Atomic uint64_t *)&ring->meta->head);
    const uint64_t tail = atomic_load((_Atomic uint64_t *)&ring->meta->tail);
    if ((head - tail) >= ring->meta->slot_count) {
        atomic_fetch_add((_Atomic uint64_t *)&ring->meta->overruns, 1);
        return EAGAIN;
    }

    const uint32_t idx = (uint32_t)(head % ring->meta->slot_count);
    view->ptr = ring->slots + ((size_t)idx * ring->meta->slot_size);
    view->seq = head;
    view->len = 0;
    return 0;
}

int gaia_memfd_ring_commit_write(struct gaia_memfd_ring *ring,
                                 const struct gaia_memfd_ring_slot_view *view,
                                 uint32_t len) {
    if (!ring || !ring->meta || !view || !gaia_slot_index_valid(ring, view->seq)) {
        return EINVAL;
    }
    if (len > ring->meta->slot_size) {
        return EMSGSIZE;
    }

    ((uint32_t *)view->ptr)[0] = len;
    atomic_thread_fence(memory_order_release);
    atomic_store((_Atomic uint64_t *)&ring->meta->head, view->seq + 1);
    return 0;
}

int gaia_memfd_ring_abort_write(struct gaia_memfd_ring *ring,
                                const struct gaia_memfd_ring_slot_view *view) {
    (void)view;
    if (!ring || !ring->meta) {
        return EINVAL;
    }
    return 0;
}

int gaia_memfd_ring_begin_read(struct gaia_memfd_ring *ring,
                               struct gaia_memfd_ring_slot_view *view) {
    if (!ring || !ring->meta || !view) {
        return EINVAL;
    }

    const uint64_t tail = atomic_load((_Atomic uint64_t *)&ring->meta->tail);
    const uint64_t head = atomic_load((_Atomic uint64_t *)&ring->meta->head);
    if (tail == head) {
        return EAGAIN;
    }

    const uint32_t idx = (uint32_t)(tail % ring->meta->slot_count);
    void *ptr = ring->slots + ((size_t)idx * ring->meta->slot_size);
    atomic_thread_fence(memory_order_acquire);
    view->ptr = ptr;
    view->seq = tail;
    view->len = ((uint32_t *)ptr)[0];
    return 0;
}

int gaia_memfd_ring_commit_read(struct gaia_memfd_ring *ring,
                                const struct gaia_memfd_ring_slot_view *view) {
    if (!ring || !ring->meta || !view) {
        return EINVAL;
    }
    atomic_store((_Atomic uint64_t *)&ring->meta->tail, view->seq + 1);
    return 0;
}
