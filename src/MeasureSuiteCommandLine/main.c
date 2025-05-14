#include <signal.h>//  sigaction
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <measuresuite.h>

/// helper struct for the python interface
typedef struct ARG_t {
	int arg_width;
	int arg_num_in;
	int arg_num_out;
	int chunksize;
	int num_batches;
	int batch_size;
} ARG;

/// helper function to print the last error
/// \param ms[in]: measuresuite_t struct
/// \param tpl_str[in]: format string of the error
void error_handling_helper_template_str(const measuresuite_t ms,
                                        const char *tpl_str) {
	const int len = 1000;
	char *s = (char *)calloc(1, len * sizeof(char));
	ms_sprintf_error(ms, s, len);
	fprintf(stderr, tpl_str, s);
	free(s);
}

/// helper function for debugging and error managment
/// \param ms[in]: measuresuite_t struct
void error_handling_helper(measuresuite_t ms) {
	error_handling_helper_template_str(ms, "Failed. Reason: %s\n");
}

/// NOTE: needs AssemblyLine, which is compiled using the "-DUSE_ASSEMBLYLINE"
    ///     make/cmake flag
/// \param asm_code[in]: the assembler code as a string not bench. 
/// \param arg
/// \return 1 on error, else 0
int bench_asm(const char *asm_code,
              const ARG *arg) {
	measuresuite_t ms = NULL;

	if (ms_initialize(&ms,
						arg->arg_width,
						arg->arg_num_in,
						arg->arg_num_out)) {
		error_handling_helper_template_str(ms,
            "Failed to ms_initialize. Reason: %s.");
		return 1;
	}

    int id = -1;
	if (ms_load_data(ms, ASM, (uint8_t *)asm_code, strlen(asm_code),
                     NULL, &id)) {
		error_handling_helper_template_str(ms,
            "Failed to measure_init. Reason: %s.");
		return 2;
	}

	// measure
	if (ms_measure(ms, 
				   arg->batch_size,
	               arg->num_batches)) {
		error_handling_helper_template_str(ms,
            "Failed to measure. Reason: %s.");
		return 3;
	}


	const char *output = NULL;
	size_t jsonlen = 0;
	ms_get_json(ms, &output, &jsonlen);

    // well just print the python stuff 
	printf("%s\n", output);

	if (ms_terminate(ms)) {
		error_handling_helper_template_str(ms,
            "Failed to measure_end. Reason: %s.");
		return 4;
	}

	return 0;
}

/// \param path[in]: path to a object *.o file
/// \param symbol[in]: symbol to bench
/// \param arg[in]: arguments
/// \return 1 on error, else 0
int bench_object(const char *path,
                 const char *symbol,
                 const ARG *arg) {
	measuresuite_t ms = NULL;
	if (ms_initialize(&ms,
						arg->arg_width,
						arg->arg_num_in,
						arg->arg_num_out)) {
		error_handling_helper_template_str(ms,
            "Failed to ms_initialize. Reason: %s.");
		printf("error 1\n");
		return 1;
	}

    int id = -1;
	if (ms_load_file(ms, ELF, path, symbol, &id)) {
		error_handling_helper_template_str(ms,
            "Failed to measure_init. Reason: %s.");
		return 2;
	}

	// measure
	if (ms_measure(ms, 
				   arg->batch_size,
	               arg->num_batches)) {
		error_handling_helper_template_str(ms,
            "Failed to measure. Reason: %s.");
		return 3;
	}

	const char *output = NULL;
	size_t jsonlen = 0;
	ms_get_json(ms, &output, &jsonlen);

    // well just print the python stuff 
	printf("%s\n", output);

	if (ms_terminate(ms)) {
		error_handling_helper_template_str(ms,
            "Failed to measure_end. Reason: %s.");
		return 4;
	}

	return 0;
}

/// \param library_path[in]: path to the .so file 
/// \param arg
/// \return 1 on error, else 0
int bench_shared_object(const char *library_path,
                        const char *symbol,
                        const ARG *arg) {
	measuresuite_t ms = NULL;
	if (ms_initialize(&ms,
						arg->arg_width,
						arg->arg_num_in,
						arg->arg_num_out)) {
		error_handling_helper_template_str(ms,
            "Failed to ms_initialize. Reason: %s.");
		return 1;
	}

    int id = -1;
	if (ms_load_file(ms, SHARED_OBJECT, library_path, symbol, &id)) {
		error_handling_helper_template_str(ms,
            "Failed to measure_init. Reason: %s.");
		return 2;
	}

	// measure
	if (ms_measure(ms, 
				   arg->batch_size,
	               arg->num_batches)) {
		error_handling_helper_template_str(ms,
            "Failed to measure. Reason: %s.");
		return 3;
	}

	const char *output = NULL;
	size_t jsonlen = 0;
	ms_get_json(ms, &output, &jsonlen);

    // well just print the python stuff 
	printf("%s\n", output);

	if (ms_terminate(ms)) {
		error_handling_helper_template_str(ms,
            "Failed to measure_end. Reason: %s.");
		return 4;
	}

	return 0;
}

/// This function compiles the given c code to a shared library.
/// NOTE: name of the library currently NOT randomized.
///  		The path `/tmp/measuresuite.so` is hardcoded
/// \param lib_path return value. Must be allocated from the caller. Will
/// 	contain the output path of the .so file
/// \param c_code input c code.
int compile_c_code(char *lib_path, 
                   const char *c_code) {
	const char *compiler_path = "cc \0";
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

/// \param c code code which will be compile to a library
/// \param asm code corresponding to the c code
int bench(const char *c_code,
		  const char *asm_code,
		  const char *symbol,
          const int arg_width,
		  const int arg_num_in,
		  const int arg_num_out) {
	ARG arg;
	arg.arg_width = arg_width;
	arg.arg_num_in = arg_num_in;
	arg.arg_num_out = arg_num_out;
	arg.chunksize = 0;
	arg.num_batches = 2;
	arg.batch_size = 2;

	// just some funny debugging:
	//printf("%s %s %s\n", c_code, asm_code, symbol);
	printf("%d %d %d\n", arg_width, arg_num_in, arg_num_out);

	char lib_path[256];
	if (compile_c_code(lib_path, c_code) != 0) {
		printf("ERROR: bench: could not compile the c_code");
		return 1;
	}

    // TODO
	// if (bench_lib(lib_path, asm_code, symbol, &arg) != 0) {
	// 	printf("ERROR: bench: could not bench\n");
	// 	return 1;
	// }

	return 0;
}


#ifdef USE_MAIN
/// EXAMPLE
/// test code for the shell
/// #include <stdint.h>
/// void add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {
/// 	*o = *i0 + *i1;
/// }
/// mov rax, [rsi]
/// add rax, [rdx]
/// mov [rdi], rax
/// ret
/// bash command
/// ./main "#include <stdint.h>
/// void add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {
///         *o = *i0 + *i1;
/// }" "mov rax, [rsi]
/// add rax, [rdx]
/// mov [rdi], rax
/// ret
/// "
///
int main(int argc, char *argv[]) {
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
#endif
