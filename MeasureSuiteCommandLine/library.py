#!/usr/bin/env python3
import argparse
import tempfile
from ctypes import *
from typing import Union
from subprocess import Popen, PIPE, STDOUT
import pathlib
import os
import json
import logging
from pathlib import Path

from .helper import DEBUG, BUILD_FOLDER, build, check_if_already_build


class Wrapper_MeasureSuiteCommandLine:
    """
    wrapper around the C wrapper I wrote. It's not a wrapper around the
    `libmeasuresuite.so` library.
    """

    def __init__(self, c_code: str, asm_code: str = "", target: str = ""):
        """
        """
        self.c_code = c_code
        self.asm_code = asm_code

        if not check_if_already_build():
            build()

        if len(c_code) == 0:
            print("please pass some c code")
            return

        if len(asm_code) == 0:
            if self.compile():
                return

        self.target = target
        self.arg_width = 1
        self.arg_num_in = 1
        self.arg_num_out = 1

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
            print(self.asm_code)
            print()
            input()

        return 0

    def run(self):
        """
        actually runs the code
        """

        c_c_code = create_string_buffer(str.encode(self.c_code))
        c_asm_code = create_string_buffer(str.encode(self.asm_code))
        c_target = create_string_buffer(str.encode(self.target))
        wrapper_lib = CDLL("build/libwrapper.so")
        wrapper_lib.bench(c_c_code, c_asm_code, c_target,
                          self.arg_width,
                          self.arg_num_in,
                          self.arg_num_out)

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
    test()
    main()
