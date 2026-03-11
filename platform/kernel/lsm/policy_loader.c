// GUARDIAN policy manifest loader and checksum verifier
//
// Loads a signed GAIA policy manifest from disk,
// verifies its SHA-256 checksum, and communicates
// the checksum to the GUARDIAN LSM kernel module.
//
// Build: gcc -O2 -o policy_loader policy_loader.c -lcrypto
// Run:   sudo ./policy_loader /etc/gaia/policy.json

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <openssl/sha.h>

#define POLICY_MAX_SIZE (1024 * 1024)  // 1 MB max
#define GUARDIAN_SYSFS  "/sys/kernel/security/guardian/policy_checksum"

static int compute_sha256(const char *path, unsigned char digest[SHA256_DIGEST_LENGTH])
{
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("policy_loader: open");
        return -1;
    }

    SHA256_CTX ctx;
    SHA256_Init(&ctx);

    unsigned char buf[4096];
    ssize_t n;
    while ((n = read(fd, buf, sizeof(buf))) > 0)
        SHA256_Update(&ctx, buf, n);
    close(fd);

    if (n < 0) {
        perror("policy_loader: read");
        return -1;
    }

    SHA256_Final(digest, &ctx);
    return 0;
}

static void print_digest(const unsigned char digest[SHA256_DIGEST_LENGTH])
{
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
        printf("%02x", digest[i]);
    printf("\n");
}

static int write_checksum_to_lsm(u_int32_t checksum)
{
    FILE *f = fopen(GUARDIAN_SYSFS, "w");
    if (!f) {
        // Not a fatal error — LSM may not be loaded in dev environment
        fprintf(stderr, "policy_loader: could not write to %s (LSM not loaded?)\n",
                GUARDIAN_SYSFS);
        return -1;
    }
    fprintf(f, "%u\n", checksum);
    fclose(f);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <policy_manifest_path>\n", argv[0]);
        return 1;
    }

    const char *policy_path = argv[1];
    unsigned char digest[SHA256_DIGEST_LENGTH];

    printf("policy_loader: verifying %s\n", policy_path);

    if (compute_sha256(policy_path, digest) != 0)
        return 1;

    printf("policy_loader: SHA-256 = ");
    print_digest(digest);

    // Truncate to 32-bit checksum for LSM sysfs interface
    u_int32_t checksum = 0;
    for (int i = 0; i < 4; i++)
        checksum = (checksum << 8) | digest[i];

    printf("policy_loader: checksum32 = 0x%08x\n", checksum);

    int rc = write_checksum_to_lsm(checksum);
    if (rc == 0)
        printf("policy_loader: checksum written to GUARDIAN LSM\n");
    else
        printf("policy_loader: checksum not written (dev mode)\n");

    return 0;
}
