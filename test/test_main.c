#include "main.c"

#define CHUNK_SIZE 100
#define NUM_BATCHES 10
#define BATCH_SIZE 100

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

ARG arg = {
    .arg_width = 1,
    .arg_num_in = 2,
    .arg_num_out = 1, 
    .chunksize = CHUNK_SIZE,
    .num_batches = NUM_BATCHES,
    .batch_size = BATCH_SIZE,
};

int test_asm_add_two_numbers() {
	const char *target = "add_two_numbers";
    return bench_asm(asm_code, &arg);
}

int test_object_add_two_numbers() {
	const char *object_file = "test.o";
	const char *symbol = "add_two_numbers";

    int ret = bench_object(object_file, symbol, &arg);
    // ret |= bench_object(object_file, NULL, &arg);
    return ret;
}

int test_shared_object_add_two_numbers() {
	const char *library_file = "test.so";
	const char *symbol = "add_two_numbers";

    return bench_shared_object(library_file, symbol, &arg);
}

int main() {
    if (test_asm_add_two_numbers()) { return 1; }
    if (test_object_add_two_numbers()) { return 1; }
    if (test_shared_object_add_two_numbers()) { return 1; }

    printf("all good\n");
    return 0;
}
