


def cli_test(): 
    """
    test command:

python MeasureSuiteCommandLine.py -c "#include <stdint.h>
void add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {
        *o = *i0 + *i1;
}" -a "mov rax, [rsi]
add rax, [rdx]
mov [rdi], rax
ret"
    """
    pass




def test():
    c_code = "#include <stdint.h>\nvoid add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {\n  *o = *i0 + *i1;\n}\n"
    asm_code = "mov rax, [rsi]\nadd rax, [rdx]\nmov [rdi], rax\nret"
    target = "add_two_numbers"

    #w = Wrapper_MeasureSuiteCommandLine(c_code, asm_code, target)
    #w = Wrapper_MeasureSuiteCommandLine(c_code, asm_code)
    w = Wrapper_MeasureSuiteCommandLine(c_code)

    w.run()

def test_static():
    """
    test the static function
    """
    c_code = """#include <stdint.h>
                void add_two_numbers(uint64_t *o, const uint64_t *i0,
                                     const uint64_t *i1) {
                    *o = *i0 + *i1;
                }"""
    asm_code = """  mov rax, [rsi]
                    add rax, [rdx]
                    mov [rdi], rax
                    ret"""
    target = "add_two_numbers"
    args_width = 1
    args_in = 2
    args_out = 1
    jdata = Wrapper_MeasureSuiteCommandLine.profile(c_code, asm_code, target, args_width, args_in,
                    args_out)
    assert jdata["stats"]
