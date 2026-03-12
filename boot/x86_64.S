// GAIA L0 Boot Entry — x86_64 Assembly stub
// Layer: L0 (Boot / Hardware Entry)
// See: docs/specs/platform/GAIALanguageStackSpecv1.0.md

.section .text.boot, "ax"
.global _gaia_boot_start
.type _gaia_boot_start, @function

_gaia_boot_start:
    // Disable interrupts during early boot
    cli

    // Set up stack pointer
    lea gaia_boot_stack_top(%rip), %rsp

    // Clear BSS segment
    lea _bss_start(%rip), %rdi
    lea _bss_end(%rip), %rcx
    sub %rdi, %rcx
    xor %eax, %eax
    rep stosb

    // Jump to C early init
    call gaia_early_init

    // Should never return
1:  hlt
    jmp 1b

.section .bss
.align 16
gaia_boot_stack:
    .space 4096
gaia_boot_stack_top:
