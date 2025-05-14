#!/usr/bin/env python3
""" wrapper around ms """

import logging
import json
import os
from pathlib import Path
from typing import Union, List, Tuple
from subprocess import Popen, PIPE, STDOUT
from types import SimpleNamespace

from .helper import _check_if_files_exists, _compile, _write_tmp_file


class MS:
    """
    wrapper around the `ms` binary
    """
    cp = os.path.dirname(os.path.realpath(__file__))
    BINARY_PATH = cp + "/deps/MeasureSuite/ms"

    def __init__(self, files: Union[List[str], List[Path]],
                 symbol_: str = ""):
        """
        Measures all provided FILE's, by calling assumed function signature 
            int (*)(uint64_t out_1[], uint64_t out_2[], ..., uint64_t in_1[], uint64_t in_2[], ...);
        :param files: path to files to compares. Each file can either be:
            - c code, asm code (intel syntax), shared object, elf file 
        :param symbol_: name of the function to execute. 
            Mandatory in case a shared object is passed
        """
        self.__symbol = ""
        self.__supported_file_types = [".so", ".o", ".c", ".asm", ".s"]
        self.__cycles = []
        self.__cmd = []
        self.__files: List[str] = []
        self.__error = False

        if not os.path.exists(MS.BINARY_PATH):
            self.__error = True
            logging.error("ms binary not found")
            return

        if len(files) < 1:
            self.__error = True
            logging.error("please pass at least a single file to the class")
            return


        self.__files = files

        # translate everything to "str"
        for i, file in enumerate(files):
            if not os.path.isfile(file):
                b, f = _write_tmp_file(file, ".asm")
                if not b:
                    self.__error = True
                    print("could not write assembly")
                    return
                self.__files[i] = f

            if isinstance(file, Path):
                self.__files[i] = str(file.absolute())

        # check if files exist
        result, _ = _check_if_files_exists(self.__files, self.__supported_file_types)
        if not result:
            self.__error = True
            return

        # check if input is correct
        for i, file in enumerate(files):
            _, file_extension = os.path.splitext(file)
            if file_extension == ".so" and len(self.__symbol) == 0:
                self.__error = True
                logging.error(".so library but no symbol given")
                return

            # compile given c files
            if file_extension == ".c":
                b, object_file = _compile(file)
                if not b:
                    self.__error = True
                    return
                self.__files[i] = object_file

        if len(symbol_) > 0:
            self.symbol(symbol_)

    def execute(self) -> Tuple[bool, dict]:
        """
        executes the internal command
        :return 
            -bool: false on error
            -dict: {
                "numFunction": number of functions tested 
                "runtime": needed time in seconds
                "incorrect": on error sets the position+1 to the function errored
                "cycles": [
                    [123,123,123,...], // func1
                    [321,321.321,...], // func2
                    ...
                ]
            }
        """
        if self.__error:
            logging.error("error available")
            return False, {}

        cmd = [self.BINARY_PATH] + self.__cmd + self.__files
        for c in cmd:
            assert isinstance(c, str)

        logging.debug(cmd)
        print(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
                   text=True, encoding="utf-8") as p:
            p.wait()
            assert p.stdout
            data = p.stdout.read()

            if p.returncode != 0:
                cmd = " ".join(cmd)
                logging.error(f"MS: {data}, couldn't execute: {data}")
                print(f"MS: {data}, couldn't execute: {data}")
                return (False, {})

        data = str(data).replace("b'", "").replace("\\n'", "").lstrip()
        data = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        data.cycles = [[float(b) for b in a] for a in data.cycles]

        self.__cycles = data.cycles
        assert len(self.__cycles) == len(self.__files)

        data.avgs = [sum(a) / len(a) for a in self.__cycles]
        data.medians = [sorted(a)[len(a) // 2] for a in self.__cycles]
        return (True, data)

    def run(self) -> Tuple[bool, dict]:
        """simple helper around execute"""
        return self.execute()

    def width(self, number: int) -> "MS":
        """ Number of elements in each array. Defaults to 10. """
        if number < 0:
            logging.error(number, "is negative")
            return self

        self.__cmd.append("--width " + str(number))
        return self

    def output(self, output: int) -> "MS":
        """
        Number of out-arrays. Defaults to 2.
        """
        if output < 0:
            logging.error(output, "is negative")
            return self

        self.__cmd.append("--out " + str(output))
        return self

    def input(self, inp: int) -> "MS":
        """
        Number of in-arrays. Defaults to 2.
        """
        if inp < 0:
            logging.error(inp, "is negative")
            return self

        self.__cmd.append("--in " + str(input))
        return self

    def num_batches(self, number: int) -> "MS":
        """
        Number of batches to measure (=number of elements in each of the result
        json's cycles-property.) Defaults to 31.
        """
        if number < 0:
            logging.error(number, "is negative")
            return self

        self.__cmd.append("--num_batches " + str(number))
        return self

    def batch_size(self, batch: int) -> "MS":
        """
        Number of iterations of each function per batch. Defaults to 150.
        """
        if batch < 0:
            logging.error(batch, "is negative")
            return self

        self.__cmd.append("--batch_size " + str(batch))
        return self

    def symbol(self, symbol: str) -> "MS":
        """
        wrapper around the `--symbol` parameter.
        `symbol` is the symbol being looked for in all .so and .o files.
        Required for .so-files. Will resort in the first found symbol in .o 
        files if `symbol` omitted.
        """
        self.__symbol = symbol
        self.__cmd.append("--symbol " + symbol)
        return self

    def check(self):
        """ wrapper """
        self.__cmd.append("--check")
        return self

    def error(self):
        """
        :return true if an error is present.
        """
        return self.__error

    def __version__(self):
        """ returns the version """
        return "1.0.0"
