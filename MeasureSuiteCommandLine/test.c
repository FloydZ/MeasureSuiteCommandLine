#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <measuresuite.h>

// a skipped test returns with 77 (based on Auto tools convention).
#define SKIP 77

// Bit position of flag from CPUID, according to Intel manual
#define ADX 19
#define BMI2 8
// the cpuid trick does not work (reliably) on the GH-CI. So we will need to use
// the SIGILL handler. Which needs a pointer to a function.
#include <signal.h> //  sigaction
#include <stdlib.h>
void error_handling_helper_template_str(measuresuite_t ms,
                                        const char *tpl_str) {
  const int len = 1000;
  char *s = calloc(1, len * sizeof(char));
  ms_str_full_error(ms, s, len);
  fprintf(stderr, tpl_str, s);
  free(s);
}

void error_handling_helper(measuresuite_t ms) {
  error_handling_helper_template_str(ms, "Failed. Reason: %s\n");
}


void exit_skip() { exit(SKIP); }
/**
 * @returns 1 if the bit is set
 */
int check_ise_bit(int bit_no) {
  // EAX value for getting the ISE's from cpu id is 07h
  int r = 0;
  int checkBit = 1 << bit_no;

  asm volatile("mov $7, %%eax \n\t"
               "mov $0, %%ecx \n\t"
               "cpuid\n\t"
               "and %%ebx, %[bit]\n\t"
               "mov %%ebx, %[ret]\n\t"
               : [ret] "=&m"(r)
               : [bit] "m"(checkBit)
               : "rax", "rbx", "rcx", "rdx");
  return r;
};

// a skipped test returns with 77 (based on Auto tools convention).
#define SKIP 77

// Bit position of flag from CPUID, according to Intel manual
#define ADX 19
#define BMI2 8

/**
 * @returns 1 if the bit is set
 */
int check_ise_bit(int bit_no);
// the cpuid trick does not work (reliably) on the GH-CI. So we will need to use
// the SIGILL handler. Which needs a pointer to a function.
#include <signal.h> //  sigaction
#include <stdlib.h>

void exit_skip();

#define SIGILL_SETUP()                                                         \
  do {                                                                         \
    if (!check_ise_bit(BMI2) || !check_ise_bit(ADX))                           \
      exit_skip();                                                             \
    struct sigaction sa;                                                       \
    sa.sa_sigaction = &exit_skip;                                              \
    sigaction(SIGILL, &sa, NULL);                                              \
  } while (0)

const char lib[] = {"./liball_lib.so"};
const char symbol[] = {"add_two_numbers"};

int main() {
  char fa[] = {"mov rax, [rsi]\n"
               "add rax, [rdx]\n"
               "mov [rdi], rax\n"
               "ret\n"};

  const int num_batches = 2;
  const int batch_size = 2;

  // INIT
  const int arg_width = 1;
  const int arg_num_in = 2;
  const int arg_num_out = 1;
  const int chunksize = 0;
  const uint64_t bounds[] = {-1};
  measuresuite_t ms = NULL;
  if (ms_measure_init(&ms, arg_width, arg_num_in, arg_num_out, chunksize,
                      bounds, lib, symbol)) {
    error_handling_helper_template_str(ms, "Failed to measure_init. Reason: %s.");
    return 1;
  }

  // measure
  if (ms_measure(ms, fa, fa, batch_size, num_batches)) {
    error_handling_helper_template_str(ms, "Failed to measure. Reason: %s.");
    return 1;
  }
  
  const char *output = NULL;
  size_t jsonlen = 0;
  ms_getJson(ms, &output, &jsonlen);
  printf("%s\n", output);

  // END
  if (ms_measure_end(ms)) {
    error_handling_helper_template_str(ms, "Failed to measure_end. Reason: %s.");
    return 1;
  }

  return 0;
}
