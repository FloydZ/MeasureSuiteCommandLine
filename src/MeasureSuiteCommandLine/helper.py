#!/usr/bin/env python3
"""
Contains helper functions and classes for measurement suite operations.
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
    Represents a result for performance measurement.

    Attributes:
        type_: Type of result - "ASM"/"OBJ"/"C"/"ELF"
        chunks: Number of chunks (only available if type is `ASM`)
    """
    type_: str
    chunks: int

    def __str__(self):
        return f"Result(type={self.type_}, chunks={self.chunks})"


class PerformanceResult:
    """
    Contains runtime results from measurement suite execution.
    """
    class Stats:
        """
        Statistics from measurement execution.

        Attributes:
            numFunctions: Number of functions measured
            runtime: Total runtime of measurement
            incorrect: Number of incorrect results
            timer: Timer type used
        """
        numFunctions: int
        runtime: float
        incorrect: int
        timer: str

    functions: List[Result]
    cycles: List[List[float]]
    medians: List[float]
    avgs: List[float]

    def __str__(self):
        return f"PerformanceResult(functions={len(self.functions)})"


class CFunction:
    """
    Tracks the number of input/outputs of a function.

    Attributes:
        arg_num_in: Number of input arguments
        arg_num_out: Number of output arguments
    """
    arg_num_in: int
    arg_num_out: int

    def __str__(self):
        return f"CFunction(in={self.arg_num_in}, out={self.arg_num_out})"


def _compile(infile: Union[str, Path]) -> Tuple[bool, str]:
    """
    Simple wrapper around `cc` to compile/assemble a given c/asm/s file.

    Args:
        infile: Path to input file to compile

    Returns:
        Tuple of (success_flag, output_file_path)
    """
    with tempfile.NamedTemporaryFile(suffix=".o", delete=False) as tmp_file:
        outfile = tmp_file.name
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
    Write data to a temporary file with the given suffix.

    Args:
        data: Content to write to the file
        suffix: File extension to use

    Returns:
        Tuple of (success_flag, file_path)
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        outfile = f.name

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(data)
        return True, outfile


def _parse(c_code: str, symbol: str = "") -> Tuple[bool, CFunction]:
    """
    Generate an AST from the given C code to extract callable functions and arguments.

    Args:
        c_code: The C code to analyze
        symbol: Optional function name to target
        
    Returns:
        Tuple of (success_flag, CFunction object)
            - True, CFunction: on success
            - False, CFunction: on any error
    """
    # A simple visitor for FuncDef nodes that prints the names and
    # locations of function definitions.
    class FuncDefVisitor(c_ast.NodeVisitor):
        """
        NodeVisitor that only processes function definitions.
        """
        def visit_func_def(self, node):
            """Process function definition nodes by extracting parameters."""
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


def build() -> int:
    """
    Builds the needed C project using CMake and Make.

    Returns:
        int: 0 on success, error code otherwise
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
               cwd=path) as p:
        p.wait()
        if p.returncode != 0:
            print("ERROR cmake")
            return 1

        # next run make
        cmd = ["make"]
        with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  cwd=path) as p:
            p.wait()
            if p.returncode != 0:
                print("ERROR make")
                return 2

    return 0


def check_if_already_build() -> bool:
    """
    Check whether `build` was called or not.
    
    Returns:
        bool: True if build folder exists, False otherwise
    """
    path = str(pathlib.Path().resolve()) + BUILD_FOLDER
    return os.path.exists(path)


def _check_if_files_exists(files: List[Any],
                        types: Union[None, List[str]] = None) -> Tuple[bool, List[Any]]:
    """
    Check if every file in the list exists and has the correct type.

    Args:
        files: List of files to check
        types: Optional list of allowed file extensions

    Returns:
        Tuple of (success_flag, files_list)
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
