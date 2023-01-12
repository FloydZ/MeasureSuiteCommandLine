	.file	"test.c"
	.text
	.p2align 4
	.globl	add_two_numbers
	.type	add_two_numbers, @function
add_two_numbers:
.LFB0:
	.cfi_startproc
	movq	(%rdx), %rax
	addq	(%rsi), %rax
	movq	%rax, (%rdi)
	ret
	.cfi_endproc
.LFE0:
	.size	add_two_numbers, .-add_two_numbers
	.ident	"GCC: (GNU) 12.2.0"
	.section	.note.GNU-stack,"",@progbits
