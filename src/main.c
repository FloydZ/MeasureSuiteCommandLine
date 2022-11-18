#include <signal.h>//  sigaction
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <measuresuite.h>

typedef struct ARG_t {
	int arg_width;
	int arg_num_in;
	int arg_num_out;
	int chunksize;
	int num_batches;
	int batch_size;
} ARG;

// helper function
void error_handling_helper_template_str(measuresuite_t ms,
                                        const char *tpl_str) {
	const int len = 1000;
	char *s = calloc(1, len * sizeof(char));
	ms_str_full_error(ms, s, len);
	fprintf(stderr, tpl_str, s);
	free(s);
}

/// helper function for debugging and error managment
void error_handling_helper(measuresuite_t ms) {
	error_handling_helper_template_str(ms, "Failed. Reason: %s\n");
}

///
/// \param c_lib path to the c lib
int bench_lib(const char *c_lib,
              const char *asm_code,
              const char *symbol,
              const ARG *arg) {
	measuresuite_t ms = NULL;

	const uint64_t bounds[] = {-1};
	if (ms_measure_init(&ms, arg->arg_width, arg->arg_num_in, arg->arg_num_out,
	                    arg->chunksize, bounds, c_lib, symbol)) {
		error_handling_helper_template_str(ms, "Failed to measure_init. Reason: %s.");
		printf("error 1\n");
		return 1;
	}

	// measure
	if (ms_measure(ms, (char *) asm_code, (char *) asm_code, arg->batch_size,
	               arg->num_batches)) {
		error_handling_helper_template_str(ms, "Failed to measure. Reason: %s.");
		printf("error 2\n");
		return 1;
	}
	const char *output = NULL;
	size_t jsonlen = 0;
	ms_getJson(ms, &output, &jsonlen);
	printf("%s\n", output);

	// END
	if (ms_measure_end(ms)) {
		// error_handling_helper_template_str(ms, "Failed to measure_end. Reason:
		// %s.");
		printf("error 3\n");
		return 1;
	}

	return 0;
}

/// This function compiles the given c code to a shared library.
/// NOTE: name of the library currently NOT randomized.
///  		The path `/tmp/measuresuite.so` is hardcoded
/// \param lib_path return value. Must be allocated from the caller. Will
/// 	contain the output path of the .so file
/// \param c_code input c code.
int compile_c_code(char *lib_path, const char *c_code) {
	const char *compiler_path = "/usr/bin/gcc \0";
	const char *compiler_flag = "-O3 -march=native -shared \0";
	const char *c_file = "/tmp/measuresuite.c";
	const char *out_cmd = "-o /tmp/measuresuite.so";

	FILE *f = fopen(c_file, "w");
	fprintf(f, "%s", c_code);
	fflush(f);
	fclose(f);

	// uff explain whats happening here
	char command[1024] = {0}, *command_ptr = command;
	strncpy(command_ptr, compiler_path, strlen(compiler_path));
	command_ptr += strlen(compiler_path);

	strncpy(command_ptr, compiler_flag, strlen(compiler_flag));
	command_ptr += strlen(compiler_flag);

	strncpy(command_ptr, c_file, strlen(c_file));
	command_ptr += strlen(c_file);
	*command_ptr = ' ';
	command_ptr++;

	strncpy(command_ptr, out_cmd, strlen(out_cmd));
	command_ptr += strlen(out_cmd);

	*command_ptr = '\0';
	// printf("%s\n", command);
	int ret = system(command);

	// write the name of the library back
	strcpy(lib_path, "/tmp/measuresuite.so");
	return ret;
}

///
/// \param c code code which will be compile to a library
/// \param asm code corresponding to the c code
int bench(const char *c_code, const char *asm_code, const char *symbol,
          const int arg_width, const int arg_num_in, const int arg_num_out) {
	ARG arg;
	arg.arg_width = arg_width;
	arg.arg_num_in = arg_num_in;
	arg.arg_num_out = arg_num_out;
	arg.chunksize = 0;
	arg.num_batches = 2;
	arg.batch_size = 2;


	char lib_path[256];
	if (compile_c_code(lib_path, c_code) != 0) {
		printf("ERROR: bench: could not compile the c_code");
		return 1;
	}

	if (bench_lib(lib_path, asm_code, symbol, &arg) != 0) {
		printf("ERROR: bench: could not bench\n");
		return 1;
	}

	return 0;
}

// just test code
int test() {
	// test code for internal usage, e.g. just pass it to the functions
	const char *asm_code = {"mov rax, [rsi]\n"
	                        "add rax, [rdx]\n"
	                        "mov [rdi], rax\n"
	                        "ret\n"};

	const char *c_code = {"#include <stdint.h>\n"
	                      "void add_two_numbers(uint64_t *o, const uint64_t *i0, "
	                      "const uint64_t *i1) {\n"
	                      "  *o = *i0 + *i1;\n"
	                      "}\n"};
	const char *target = "add_two_numbers";
	const int arg_width = 1;
	const int arg_num_in = 2;
	const int arg_num_out = 1;

	return bench(c_code, asm_code, target, arg_width, arg_num_in, arg_num_out);
}

int main(int argc, char *argv[]) {
	// test code for the shell
	// #include <stdint.h>
	// void add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {
	// 	*o = *i0 + *i1;
	// }
	// mov rax, [rsi]
	// add rax, [rdx]
	// mov [rdi], rax
	// ret


	// bash command
	// ./main "#include <stdint.h>
	// void add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {
	//         *o = *i0 + *i1;
	// }" "mov rax, [rsi]
	// add rax, [rdx]
	// mov [rdi], rax
	// ret
	// "

	// check if we are in the simple test mode
	if (argc == 2 && (strncmp(argv[1], "--test", 6) == 0)) {
		return test();
	}
	
	// check for correct inputs
	if (argc != 7) {
		printf("arguments:`c_code` `asm_code`, `target`, `arg_width`, `arg_num_in`, `arg_num_out`\n");
		printf("or: --test");
		return 1;
	}

	const char *c_code = argv[1];
	const char *asm_code = argv[2];
	const char *target = argv[3];
	const int arg_width = atoi(argv[4]);
	const int arg_num_in = atoi(argv[5]);
	const int arg_num_out = atoi(argv[6]);

	return bench(c_code, asm_code, target, arg_width, arg_num_in, arg_num_out);
}
