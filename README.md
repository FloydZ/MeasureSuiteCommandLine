Wrapper around [MeasureSuite](https://github.com/0xADE1A1DE/MeasureSuite).
In fact there are two wrappers. First a simple C commandline interface, which
allows you to pass `C` code and the coresponding `asm` block. The programm then
compiles automatically the needed shared library for `MeasureSuite` and runs
it. This simple commandline interface is then again wrapped in a python library
which allows for an even easier usage.

Build:
----
Run:
```bash
git clone --recursive https://github.com/FloydZ/MeasureSuiteCommandLine
cd MeasureSuiteCommandLine
mkdir -p build
cd build
cmake ..
make
```
and that should do it.

C Interface
----
After you build the libray a binary `main` is available in `build`. Use it like
so:
```bash
./main "#include <stdint.h>
void add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) { 
        *o = *i0 + *i1;
}" "mov rax, [rsi] 
add rax, [rdx] 
mov [rdi], rax
ret
"
```

After everything run successfull you should see the output:
```json    
{
"stats":
  {
   "countA": 1,
   "countB": 1,
   "chunksA": 0,
   "chunksB": 0,
   "batchSize": 1,
   "numBatches": 1,
   "runtime": 0,
   "runOrder": "ba",
   "checkResult": true
   },
"times": [[-1,4792,1196],[798,-1,771]]
}
```

Python Wrapper:
---

```python
c_code = "#include <stdint.h>\nvoid add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {\n  *o = *i0 + *i1;\n}\n"
w = Wrapper_MeasureSuiteCommandLine(c_code)
w.run()
```

TODOs:
======
- [ ] C Lib: wrap the interface to only benchmark a single function
- [ ] python also compile to .so file, is probably the easiest.
