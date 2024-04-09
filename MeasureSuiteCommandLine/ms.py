#!/usr/bin/env python3
""" wrapper around ms """
import logging
import json
import os
from pathlib import Path
from typing import Union
from subprocess import Popen, PIPE, STDOUT
from types import SimpleNamespace
from .helper import _check_if_files_exists, _compile


class MS:
    """
    wrapper around the `ms` binary
    """
    BINARY_PATH = "deps/MeasureSuite/ms"

    def __init__(self, files: list[Union[str, Path]],
                 symbol_: str = ""):
        """
        Measures all provided FILE's, by calling assumed function signature 
            int (*)(uint64_t out_1[], uint64_t out_2[], ..., uint64_t in_1[], uint64_t in_2[], ...);
        """
        self.__symbol = ""
        self.__supported_file_types = [".so", ".o", ".c", ".asm", ".s"]
        self.__cycles = []
        self.__cmd = []
        self.__files = []
        self.__error = False

        if not os.path.exists(MS.BINARY_PATH):
            self.__error = True
            logging.error("ms binary not found")
            return

        if len(files) < 1:
            self.__error = True
            logging.error("please pass at least a single file to the class")
            return

        result, files = _check_if_files_exists(files, self.__supported_file_types)
        if not result:
            self.__error = True
            return

        # compile given c files
        for i, file in enumerate(files):
            _, file_extension = os.path.splitext(file)
            if file_extension == ".c":
                result, outfile = _compile(file)
                if not result:
                    self.__error = True
                    logging.error("could not compile: %s", file)
                    return

                files[i] = outfile

            _, file_extension = os.path.splitext(file)
            if file_extension == ".so" and len(self.__symbol) == 0:
                self.__error = True
                logging.error(".so library but no symbol given")
                return

        if len(symbol_) > 0:
            self.symbol(symbol_)

        self.__files = files

    def execute(self):
        """
        executes the internal command
        :return bool: false on error
        """
        if self.__error:
            logging.error("error available")
            return False

        cmd = [self.BINARY_PATH] + self.__cmd + self.__files
        for c in cmd:
            assert isinstance(c, str)

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

    def error(self):
        """
        :return true if an error is present.
        """
        return self.__error

    def __version__(self):
        """ returns the version """
        return "1.0.0"
