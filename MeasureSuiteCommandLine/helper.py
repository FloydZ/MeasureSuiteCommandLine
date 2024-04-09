#!/usr/bin/env python3
from subprocess import Popen, PIPE, STDOUT
from pycparser import c_ast, parse_file
from pathlib import Path
import os
import logging
import pathlib
import tempfile


OPT_FLAGS = ["-O3", "-march=native"]
CC = "cc"
BUILD_FOLDER = "/build"
DEBUG = True


class Result:
    """
    needed for `PerformanceResult`
    type: "ASM"/"OBJ"/"C"/"ELF"
    chunks: only available if type is `ASM`
    """
    type_: str
    chunks: int


class PerformanceResult:
    """
    runtime result = output of MS
    """
    class Stats:
        """
        """
        numFunctions: int
        runtime: float
        incorrect: int
        timer: str

    functions: list[Result]
    cycles: list[list[float]]
    medians: list[float]
    avgs: list[float]


class CFunction:
    """
    tracks the number of input/outputs of a function
    """
    arg_num_in: int
    arg_num_out: int


def _compile(infile: str):
    """
    simple wrapper around `cc` to compile/assemble a given c/asm/s file.
    """
    outfile = tempfile.NamedTemporaryFile(suffix=".o").name
    flags = ["-o", outfile, "-c", infile]
    cmd = [CC] + flags + OPT_FLAGS
    logging.debug(cmd)
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
              text=True, encoding="utf-8")
    p.wait()
    assert p.stdout

    data = p.stdout.read()
    data = str(data).replace("b'", "").replace("\\n'", "").lstrip()
    if p.returncode != 0:
        logging.error("MS: could not compile: %s %s", " ".join(cmd), data)
        return False, outfile

    return True, outfile


def _parse(c_code: str, symbol: str = ""):
    """
    this function is called to generate a `AST` from the given C code
    to extract the callable functions and its arguments

    :param c_code the c code to analyse
    :param symbol

    :return True, CFunction:  on success
            False, CFunction: on any error
    """
    # A simple visitor for FuncDef nodes that prints the names and
    # locations of function definitions.
    class FuncDefVisitor(c_ast.NodeVisitor):
        def visit_FuncDef(self, node):
            names = [n.name for n in node.decl.type.args.params]
            types = [n.type.type.type.names for n in node.decl.type.args.params]
            const = [n.type.type.quals for n in node.decl.type.args.params]
            funcs[node.decl.name] = {
                "nr_args": len(node.decl.type.args.params),
                "names:": names,
                "types": types,
                "const": const
            }

    f = tempfile.NamedTemporaryFile(delete=False)
    name = f.name
    f.write(c_code.encode())
    f.flush()
    f.close()

    c = CFunction()
    funcs = {}
    ast = parse_file(name, use_cpp=True)
    v = FuncDefVisitor()
    v.visit(ast)
    logging.debug("parsed functions: %s", funcs)

    if symbol == "" and len(list(funcs.keys())) > 1:
        logging.error("Multiple Symbols found, cannot choose the correct one")
        return False, c

    # set the target
    if symbol == "" and len(list(funcs.keys())) == 1:
        symbol = list(funcs.keys())[0]
        logging.debug("symbol set to: %s", symbol)

    # well this is going to be a problem source
    if funcs[symbol]["nr_args"] == 0:
        c.arg_num_in = 0
        c.arg_num_out = 0
    elif funcs[symbol]["nr_args"] == 1:
        c.arg_num_in = 1
        c.arg_num_out = 0
    elif funcs[symbol]["nr_args"] > 1:
        c.arg_num_in = funcs[symbol]["nr_args"] - 1
        c.arg_num_out = 1

    return True, c


def _parse_asm(asm_code: str, symbol: str = ""):
    """
    :param asm_code the asm code to analyse
    :param symbol

    :return True, CFunction:  on success
            False, CFunction: on any error
    """
    # TODO not implemented
    c = CFunction()
    return False, c


def build():
    """
    simply builds the needed C project.
    """
    # first create the build folder
    path = str(pathlib.Path().resolve())
    path += BUILD_FOLDER
    os.mkdir(path)

    if DEBUG:
        print("build:", path)

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
    checks whether `build` was called or not.
    """
    path = str(pathlib.Path().resolve()) + BUILD_FOLDER
    return os.path.exists(path)


def _check_if_ccode_or_asmcode(array: list):
    """
    checks if any element in `array` is either valid c code or asm code.
    If successfully detected it will also automatically compile/assemble it
    and replaces the entry with a temporary object file.

    NOTE: call this function before you call `_check_if_files_exists`
    :param array
    :return
    """
    if len(array) == 0:
        logging.debug("no input")
        return True, []

    ret = [CFunction]*len(array)
    for i, a in enumerate(array):
        if isinstance(a, str):
            # first try to parse it as a C file
            status, cf = _parse(a)
            if status:
                # first write back: argument information about
                ret[i] = cf

                # next write the c code into a tmp file
                cfile = tempfile.NamedTemporaryFile(suffix=".c")
                cfile.write(a)
                cfile.flush()
                cfile.close()
                status2, outfile = _compile(cfile.name)
                if status2:
                    array[i] = outfile
                    continue
                else:
                    logging.error("couldn't compile c file")
                    return False, ret

            # try to assemble file
            status, cf = _parse_asm(a)
            if status:
                ret[i] = cf
                cfile = tempfile.NamedTemporaryFile(suffix=".asm")
                cfile.write(a)
                cfile.flush()
                cfile.close()
                status2, outfile = _compile(cfile.name)
                if status2:
                    array[i] = outfile
                    continue
                else:
                    logging.error("couldn't assemble asm file")
                    return False, ret

    return True, ret


def _check_if_files_exists(files: list, types=[]):
    """
    check if every file in `files` exists and (if given) it's of any
    type given in `types`.
    :param: files list of files to check
    :param: types
    """
    for i, file in enumerate(files):
        if isinstance(file, Path):
            files[i] = file.absolute()

    for i, file in enumerate(files):
        if not os.path.exists(file):
            return False, files

        _, file_extension = os.path.splitext(file)
        if file_extension not in types:
            logging.error("Dont know this file type: %s", file_extension)
            return False, files
    return True, files


