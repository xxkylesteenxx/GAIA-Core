/*
 * gaia_stage0_entry.S
 * Minimal x86_64 research-only stage-0 entry.
 * This is NOT a complete bootloader. It only shows the earliest control-transfer
 * shape for a custom bring-up path.
 */

.section .text
.global _start
.type _start, @function

_start:
    cli

    /* Establish a temporary stack. */
    lea stack_top(%rip), %rsp
    xor %rbp, %rbp

    /* Call C stage-1 bring-up. */
    call gaia_stage1_main

.hang:
    hlt
    jmp .hang

.section .bss
.align 16
stack_bottom:
    .skip 16384
stack_top:
