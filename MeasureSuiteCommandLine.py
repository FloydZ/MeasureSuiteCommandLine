from subprocess import Popen, PIPE, STDOUT
import argparse
import os
import pathlib
import json
import pycparser
import tempfile
from pycparser import c_ast, parse_file


BUILD_FOLDER = "/build"
DEBUG = True 


def build():
    """
    simply builds the needed C project.
    """
    # first create the build folder
    path = str(pathlib.Path().resolve())
    path += BUILD_FOLDER
    os.mkdir(path)

    if DEBUG:
        print(path)

    # next run the cmake command
    cmd = ["cmake", ".."]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              preexec_fn=os.setsid, cwd=path)
    p.wait()
    if p.returncode != 0:
        print("ERROR cmake")
        return 1

    # next run make
    cmd = ["make"]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              preexec_fn=os.setsid, cwd=path)
    p.wait()
    if p.returncode != 0:
        print("ERROR make")
        return 2

    return 0


def check_if_already_build():
    """
    checks wether `build` was called or not.
    """
    path = str(pathlib.Path().resolve()) + BUILD_FOLDER
    return os.path.exists(path)


def profile(c_code: str, asm_code: str, target: str, arg_width: int,
            arg_num_in: int, arg_num_out: int):
    """
    runs the c code
    """
    # run the c code
    cmd = ["./main", c_code, asm_code, target, str(arg_width), str(arg_num_in),
           str(arg_num_out)]
    path = str(pathlib.Path().resolve()) + BUILD_FOLDER
    if DEBUG:
        print(cmd, path, type(path))
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              preexec_fn=os.setsid, cwd=path)
    p.wait()

    # read the output
    data = p.stdout.read()
    data = data.decode("ascii")
    if DEBUG:
        print(data)

    # example output of the programm
    # {
    #   "stats":
    #  {
    #   "countA": 1,
    #   "countB": 1,
    #   "chunksA": 0,
    #   "chunksB": 0,
    #   "batchSize": 1,
    #   "numBatches": 1,
    #   "runtime": 0,
    #   "runOrder": "ba",
    #   "checkResult": true
    #   },
    #  "times": [[-1,4792,1196],[798,-1,771]]
    #  }
    jdata = json.loads(data)
    return jdata


def parse_c_code(c_code: str, target: str):
    """
    parses c code and finds out how many functions are defined.
    """
    # A simple visitor for FuncDef nodes that prints the names and
    # locations of function definitions.
    class FuncDefVisitor(c_ast.NodeVisitor):
        def visit_FuncDef(self, node):
            # print('%s at %s' % (node.decl.name, node.decl.coord))
            names = [n.name for n in node.decl.type.args.params]
            types = [n.type.type.type.names for n in node.decl.type.args.params]
            const = [n.type.type.quals for n in node.decl.type.args.params]
            # print(node.decl.type.args)
            funcs[node.decl.name] = {
                    "nr_args": len(node.decl.type.args.params),
                    "names:": names,
                    "types": types,
                    "const": const
                    }

    f = tempfile.NamedTemporaryFile(delete=False)
    name = f.name
    f.write(c_code.encode())
    f.close()

    funcs = {}
    ast = pycparser.parse_file(name, use_cpp=True)
    v = FuncDefVisitor()
    v.visit(ast)

    if target is None and len(list(funcs.keys())) == 1:
        target = list(funcs.keys())[0]

    # TODO
    print(funcs)
    return target, 1, 1, 1


def main():
    parser = argparse.ArgumentParser(description='MeasureSuiteCommandLine')
    parser.add_argument('-c', required=False, type=str, help='c code')
    parser.add_argument('-a', required=False, type=str, help='asm code')
    parser.add_argument('-cf', required=False, type=str, help='c code file')
    parser.add_argument('-af', required=False, type=str, help='asm code file')
    parser.add_argument('-t', required=False, type=str, help='target')
    args = parser.parse_args()

    # check wether the c project was build or not
    if not check_if_already_build():
        if build() != 0:
            print("could not build the c projext")

    if not args.c and not args.cf:
        print("please pass c code")

    if not args.a and not args.af:
        print("please pass asm code")

    if args.cf:
        with open(args.cf) as f:
            args.c = f.read()

    if args.af:
        with open(args.af) as f:
            args.a = f.read()

    target, arg_width, arg_num_in, arg_num_out = parse_c_code(args.c, args.t)
    jdata = profile(args.c, args.a, target, arg_width, arg_num_in,
                    arg_num_out)
    print(jdata)


if __name__ == "__main__":
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
    main()
