#!/usr/bin/env python3
"""
contains helper function regarding 
"""
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import List, Union, Tuple, Any
import os
import logging
import pathlib
import tempfile
from pycparser import c_ast, parse_file


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

    functions: List[Result]
    cycles: List[List[float]]
    medians: List[float]
    avgs: List[float]


class CFunction:
    """
    tracks the number of input/outputs of a function
    """
    arg_num_in: int
    arg_num_out: int


def _compile(infile: Union[str, Path]) -> Tuple[bool, str]:
    """
    simple wrapper around `cc` to compile/assemble a given c/asm/s file.
    """
    outfile = tempfile.NamedTemporaryFile(suffix=".o").name
    flags = ["-o", outfile, "-c", infile]
    cmd = [CC] + flags + OPT_FLAGS
    logging.debug(cmd)
    with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
               text=True, encoding="utf-8") as p:
        p.wait()
        assert p.stdout

        data = p.stdout.read()
        data = str(data).replace("b'", "").replace("\\n'", "").lstrip()
        if p.returncode != 0:
            logging.error("MS: could not compile: %s %s", " ".join(cmd), data)
            return False, outfile

        return True, outfile


def _write_tmp_file(data: str, suffix=".asm") -> Tuple[bool, str]:
    """
    :param data:
    :param suffix:
    :return
    """
    outfile = tempfile.NamedTemporaryFile(suffix=suffix).name
    with open(outfile, "w") as f:
        f.write(data)
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
        """
        this class allows us to only visit function
        """
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

    with tempfile.NamedTemporaryFile(delete=False) as f:
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
    with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
               preexec_fn=os.setsid, cwd=path) as p:
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


def _check_if_files_exists(files: List[Any], types: Union[None, List[str]]=None):
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
        if types is not None and file_extension not in types:
            logging.error("Dont know this file type: %s", file_extension)
            return False, files
    return True, files
