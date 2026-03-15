#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <liburing.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/eventfd.h>
#include <sys/types.h>
#include <unistd.h>

struct gaia_uring_runtime {
    struct io_uring ring;
    int event_fd;
    bool started;
};

struct gaia_uring_op {
    uint64_t user_data;
    void *buffer;
    unsigned length;
    off_t offset;
};

int gaia_uring_runtime_init(struct gaia_uring_runtime *rt, unsigned depth) {
    if (!rt || depth == 0) {
        return EINVAL;
    }
    memset(rt, 0, sizeof(*rt));

    int rc = io_uring_queue_init((unsigned)depth, &rt->ring, IORING_SETUP_CLAMP);
    if (rc < 0) {
        return -rc;
    }

    rt->event_fd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (rt->event_fd < 0) {
        rc = errno;
        io_uring_queue_exit(&rt->ring);
        return rc;
    }

    rc = io_uring_register_eventfd(&rt->ring, rt->event_fd);
    if (rc < 0) {
        close(rt->event_fd);
        io_uring_queue_exit(&rt->ring);
        return -rc;
    }

    rt->started = true;
    return 0;
}

void gaia_uring_runtime_shutdown(struct gaia_uring_runtime *rt) {
    if (!rt || !rt->started) {
        return;
    }
    io_uring_unregister_eventfd(&rt->ring);
    close(rt->event_fd);
    io_uring_queue_exit(&rt->ring);
    memset(rt, 0, sizeof(*rt));
}

static int gaia_uring_submit_common(struct gaia_uring_runtime *rt,
                                    int fd,
                                    const struct gaia_uring_op *op,
                                    bool write_op) {
    if (!rt || !rt->started || fd < 0 || !op || !op->buffer || op->length == 0) {
        return EINVAL;
    }

    struct io_uring_sqe *sqe = io_uring_get_sqe(&rt->ring);
    if (!sqe) {
        return EBUSY;
    }

    if (write_op) {
        io_uring_prep_write(sqe, fd, op->buffer, op->length, op->offset);
    } else {
        io_uring_prep_read(sqe, fd, op->buffer, op->length, op->offset);
    }
    io_uring_sqe_set_data64(sqe, op->user_data);

    int rc = io_uring_submit(&rt->ring);
    return rc < 0 ? -rc : 0;
}

int gaia_uring_submit_read(struct gaia_uring_runtime *rt, int fd, const struct gaia_uring_op *op) {
    return gaia_uring_submit_common(rt, fd, op, false);
}

int gaia_uring_submit_write(struct gaia_uring_runtime *rt, int fd, const struct gaia_uring_op *op) {
    return gaia_uring_submit_common(rt, fd, op, true);
}

int gaia_uring_wait_cqe(struct gaia_uring_runtime *rt, struct io_uring_cqe **cqe) {
    if (!rt || !rt->started || !cqe) {
        return EINVAL;
    }
    const int rc = io_uring_wait_cqe(&rt->ring, cqe);
    return rc < 0 ? -rc : 0;
}

void gaia_uring_cqe_seen(struct gaia_uring_runtime *rt, struct io_uring_cqe *cqe) {
    if (rt && rt->started && cqe) {
        io_uring_cqe_seen(&rt->ring, cqe);
    }
}
