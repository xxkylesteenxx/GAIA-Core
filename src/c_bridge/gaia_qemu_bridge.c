// SPDX-License-Identifier: GPL-2.0
/*
 * gaia_qemu_bridge.c
 *
 * Minimal QMP Unix socket client for the GAIA C bridge layer.
 *
 * This file provides the lowest-level socket plumbing only.
 * JSON construction, QMP capability negotiation, and command
 * sequencing are the responsibility of the Rust VMM caller.
 *
 * Trust model: QEMU is NOT a trust boundary. This bridge is a
 * one-way command channel from the Rust VMM to QEMU only.
 *
 * Spec ref: VIRT-MEM-IPC-SPEC §3.5, §8
 */

#include "gaia_qemu_bridge.h"

#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

int gaia_qmp_open(const char *unix_socket_path)
{
    int fd;
    struct sockaddr_un addr;

    if (!unix_socket_path || unix_socket_path[0] == '\0')
        return -1;

    fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0)
        return -1;

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, unix_socket_path, sizeof(addr.sun_path) - 1);
    /* addr.sun_path is always null-terminated: strncpy zero-fills remainder */

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        close(fd);
        return -1;
    }

    return fd;
}

int gaia_qmp_send_raw(int fd, const char *json_line)
{
    size_t  len;
    ssize_t rc;

    if (fd < 0 || !json_line)
        return -1;

    len = strlen(json_line);
    if (len == 0)
        return -1;

    rc = write(fd, json_line, len);
    return (rc == (ssize_t)len) ? 0 : -1;
}

int gaia_qmp_close(int fd)
{
    if (fd < 0)
        return -1;
    return close(fd);
}
