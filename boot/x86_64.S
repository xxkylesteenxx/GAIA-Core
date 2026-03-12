/* GAIA L0 Boot Stub — x86_64
 * Layer: L0 — Boot / Hardware Entry
 * Language: Assembly
 * Purpose: Early CPU handoff from UEFI to GAIA kernel entry point.
 *
 * This stub is executed after UEFI hands off control.
 * It prepares the CPU state (long mode confirmed, stack set),
 * clears BSS, and jumps to the C/Rust kernel entry.
 */

.section .text
.global _gaia_boot_start
.extern gaia_kernel_entry

_gaia_boot_start:
    /* Disable interrupts during early boot */
    cli

    /* Set up a minimal stack pointer */
    lea     gaia_boot_stack_top(%rip), %rsp

    /* Zero out BSS segment */
    lea     __bss_start(%rip), %rdi
    lea     __bss_end(%rip), %rcx
    sub     %rdi, %rcx
    xor     %eax, %eax
    rep     stosb

    /* Jump to C/Rust kernel entry — does not return */
    call    gaia_kernel_entry

    /* Halt if kernel entry returns (should never happen) */
_gaia_halt:
    hlt
    jmp     _gaia_halt

/* Boot-time stack: 16KB */
.section .bss
.align 16
gaia_boot_stack:
    .space 16384
gaia_boot_stack_top:
