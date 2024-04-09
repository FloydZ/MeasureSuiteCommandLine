#!/usr/bin/env python3
import argparse
import ctypes
from pycparser import c_ast, parse_file
import tempfile
from ctypes import *
from typing import Union
from subprocess import Popen, PIPE, STDOUT
import pathlib
import os
import json
import logging
from enum import Enum
from pathlib import Path

from .helper import DEBUG, BUILD_FOLDER, build, check_if_already_build
BUILD_FOLDER = "/build"
DEBUG = True

class InputType(Enum):
    ASM = 1,
    C = 2,

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


class Library:
    """
    wrapper around the C wrapper I wrote. It's not a wrapper around the
    `libmeasuresuite.so` library.
    """

    def __init__(self, c_code: str, asm_code: str = "", target: str = ""):
    MEASURESUITELIBRARY = "deps/MeasureSuite/lib/libmeasuresuite.so"

    def __init__(self, c_code: str = "", asm_code: str = "", target: str = ""):
        """
        TODO: pass number of arguments, type of arguments.
        TODO: allow .so as input
        """
        self.asm_code = asm_code

        if not check_if_already_build():
            build()

        if len(c_code) == 0:
            print("please pass some c code")
            return

        if len(asm_code) == 0:
            if self.compile():
                return

        self.c_code = None
        
        if len(c_code) != 0:
            self.c_code = c_code
            if not self.compile():
                return

        if len(asm_code) != 0:
            self.asm_code = asm_code
        
        self.target = target
        self.arg_width = 1
        self.arg_num_in = 2
        self.arg_num_out = 1
        self.number_of_batches = 10 
        self.batch_size = 100

        if len(self.target) == 0:
            if self.parse():
                return
        # self.run()

    def compile(self):
        """
        if the asm code is not passed, this function will generate it.
        
        TODO NOTE about the inputs (asm syntax, etc )

        :return 0 on success
                1 on any error
        """

        inf = tempfile.NamedTemporaryFile(mode="w+", suffix=".c")
        outf = tempfile.NamedTemporaryFile(mode="w+", suffix=".asm")
        cmd = ["gcc", "-S", "-masm=intel", inf.name, "-o", outf.name]

        inf.write(self.c_code)
        inf.flush()

        if DEBUG:
            print(cmd)
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

        p.wait()
        if p.returncode != 0:
            assert p.stdout
            print("ERROR could not assemble:", p.returncode,
                  p.stdout.read().decode("utf-8"))
            return p.returncode

        lines = outf.readlines()
        lines = [
            str(a)
            .replace("b'", "")
            .replace("\\n'", "")
            .lstrip()
            .replace("PTR", "")
            .replace("QWORD", "")
            .replace("DWORD", "")
            .replace("WORD", "")
            .replace("BYTE", "")
            for a in lines
        ]

        def check_words(line):
            l = [".file", ".intel_syntax", ".text", ".p2align", ".globl",
                 ".type", ".size", ".ident", ".section", ".cfi"]
            for w in l:
                if w in line:
                    return False

            return True

        lines = filter(check_words, lines)
        self.asm_code = "".join(lines)

        if DEBUG:
            print("asm code")
            print(self.asm_code)

        return True

    def run(self):
        """
        actually runs the code of my library
        """

        c_c_code = create_string_buffer(str.encode(self.c_code))
        c_asm_code = create_string_buffer(str.encode(self.asm_code))
        c_target = create_string_buffer(str.encode(self.target))
        wrapper_lib = CDLL("build/libwrapper.so")
        wrapper_lib.bench(c_c_code, c_asm_code, c_target,
                          self.arg_width,
                          self.arg_num_in,
                          self.arg_num_out)
    def run_library(self):
        """This runs the code of the `MeasureSuiteLibrary`"""
        if self.asm_code is None:
            print("no assembly code")
            return 

        lib = CDLL(Library.MEASURESUITELIBRARY) 
        ms = create_string_buffer(1024)
        # ms = ctypes.c_void_p(t)
        
        tmp = str.encode(self.asm_code)
        c_asm_code = create_string_buffer(tmp)
        id = -1
        lib.ms_initialize(ms, self.arg_width, self.arg_num_in, self.arg_num_out)
        print("init")

        lib.ms_load_data(ms, InputType.ASM, c_asm_code, len(tmp), c_void_p(0), pointer(id))
        print("load")
        
        lib.ms_measure(ms, self.batch_size, self.number_of_batches)
        print("measure")
        
        j = ctypes.c_void_p(0)
        l = 0
        lib.ms_get_json(ms, j, pointer(l))
        print("json")

        for i in range(128):
            print(ms[i])

    @staticmethod
    def profile(c_code: str,
                asm_code: str,
                target: str,
                arg_width: int,
                arg_num_in: int,
                arg_num_out: int):
        """
        static functions
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

        assert p.stdout

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


def main():
    # TODO simplify interface
    parser = argparse.ArgumentParser(description='MeasureSuiteCommandLine')
    parser.add_argument('-c', required=False, type=str, help='c code')
    parser.add_argument('-a', required=False, type=str, help='asm code')
    parser.add_argument('-cf', required=False, type=str, help='c code file')
    parser.add_argument('-af', required=False, type=str, help='asm code file')
    parser.add_argument('-t', required=False, type=str, help='target')
    args = parser.parse_args()

    # check whether the c project was build or not
    if not check_if_already_build():
        if build() != 0:
            print("could not build the c projext")

    # check if passes
    if not args.c and not args.cf:
        print("please pass c code")
        exit(1)

    if not args.a and not args.af:
        print("please pass asm code")
        exit(2)

    if args.cf:
        with open(args.cf) as f:
            args.c = f.read()

    if args.af:
        with open(args.af) as f:
            args.a = f.read()

    target, arg_width, arg_num_in, arg_num_out = parse_c_code(args.c, args.t)
    jdata = Wrapper_MeasureSuiteCommandLine.profile(args.c, args.a, target, arg_width, arg_num_in,
                                                    arg_num_out)

    print(jdata)


if __name__ == '__main__':
    main()
