#!/usr/bin/env python3
""" wrapper around ms """
import logging
import json
import os
import tempfile
from pathlib import Path
from typing import Union
from subprocess import Popen, PIPE, STDOUT
from types import SimpleNamespace


class Result:
    """ kp """
    type_: str


class PerformaceResult:
    """ still wip """
    class Stats:
        """ still wip """
        numFunctions: int
        runtime: float
        incorrect: int
        timer: str

    functions: list[Result]
    cycles: list[list[float]]
    medians: list[float]
    avgs: list[float]



class Ms:
    """
    wrapper around the `ms` binary
    """

    BINARY_PATH = "deps/MeasureSuite/ms"
    OPT_FLAGS = ["-O3", "-march=native"]
    CC = "cc"

    def __init__(self, files: list[Union[str, Path]]):
        """
        Measures all provided FILE's, by calling assumed function signature 
            int (*)(uint64_t out_1[], uint64_t out_2[], ..., uint64_t in_1[], uint64_t in_2[], ...);

        """
        self.__symbol = ""
        self.__supported_file_types = [".so", ".o", ".c", ".asm", ".s"]
        self.__cycles = []
        self.__cmd = []
        self.__files = files
        for i, file in enumerate(files):
            if isinstance(file, Path):
                self.__files[i] = file.absolute()

        for i, file in enumerate(self.__files):
            _, file_extension = os.path.splitext(file)
            if file_extension not in self.__supported_file_types:
                logging.error("Dont know this file type: %s", file_extension)
                return

            if file_extension == ".c":
                outfile = tempfile.NamedTemporaryFile(suffix=".o").name
                if not self.compile(outfile, file):
                    logging.error("could not compile: %s", file)
                    return

                self.__files[i] = outfile

        if len(self.__files) < 1:
            logging.error("please pass at least a single file to the class")

    def compile(self, outfile: str, infile: str):
        """
        simple wrapper around `cc` to compile a given c file.
        """
        flags = ["-o", outfile, "-c", infile]
        cmd = [Ms.CC] + flags + Ms.OPT_FLAGS
        logging.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
                  text=True, encoding="utf-8")
        p.wait()
        assert p.stdout

        data = p.stdout.read()
        data = str(data).replace("b'", "").replace("\\n'", "").lstrip()
        print(data)
        if p.returncode != 0:
            logging.error("MS: could not compile: %s", " ".join(cmd))
            return False

        return True

    def execute(self):
        """
        executes the internal command
        :return false on error
        """
        if len(self.__files) < 1:
            logging.error("please pass at least a single file to the class")
            return False

        cmd = [self.BINARY_PATH] + self.__cmd + self.__files
        for c in cmd:
            assert isinstance(c, str)

        # make sure that, given a `.so` library that a symbol is given:
        for file in self.__files:
            _, file_extension = os.path.splitext(file)
            if file_extension == ".so" and len(self.__symbol) == 0:
                logging.error(".so library but no symbol given")
                return False

        logging.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
                  text=True, encoding="utf-8")
        p.wait()
        assert p.stdout

        if p.returncode != 0:
            logging.error("MS: couldn't execute: %s", " ".join(cmd))
            print(p.stdout.read())
            return False

        data = p.stdout.read()
        data = str(data).replace("b'", "").replace("\\n'", "").lstrip()
        data = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        data.cycles = [[float(b) for b in a] for a in data.cycles]

        self.__cycles = data.cycles
        assert len(self.__cycles) == len(self.__files)

        data.avgs = [sum(a) / len(a) for a in self.__cycles]
        data.medians = [sorted(a)[len(a) // 2] for a in self.__cycles]

        print(data)
        return data

    def run(self):
        """simple helper around execute"""
        return self.execute()

    def width(self, number: int):
        """ Number of elements in each array. Defaults to 10. """
        if number < 0:
            logging.error(number, "is negative")
            return

        self.__cmd.append("--width " + str(number))

    def output(self, output: int):
        """
        Number of out-arrays. Defaults to 2.
        """
        if output < 0:
            logging.error(output, "is negative")
            return

        self.__cmd.append("--out " + str(output))

    def input(self, inp: int):
        """
        Number of in-arrays. Defaults to 2.
        """
        if inp < 0:
            logging.error(inp, "is negative")
            return

        self.__cmd.append("--in " + str(input))

    def num_batches(self, number: int):
        """
        Number of batches to measure (=number of elements in each of the result
        json's cycles-property.) Defaults to 31.
        """
        if number < 0:
            logging.error(number, "is negative")
            return

        self.__cmd.append("--num_batches " + str(number))

    def batch_size(self, batch: int):
        """
        Number of iterations of each function per batch. Defaults to 150.
        """
        if batch < 0:
            logging.error(batch, "is negative")
            return

        self.__cmd.append("--batch_size " + str(batch))

    def symbol(self, symbol: str):
        """
        wrapper around the `--symbol` parameter.
        `symbol` is the symbol being looked for in all .so and .o files.
        Required for .so-files. Will resort in the first found symbol in .o 
        files if `symbol` omitted.
        """
        self.__symbol = symbol
        self.__cmd.append("--symbol " + symbol)

    def check(self):
        """ wrapper """
        self.__cmd.append("--check")

    def __version__(self):
        """ returns the version """
        return "1.0.0"
