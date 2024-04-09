#!/usr/bin/env python3
""" wrapper around `MSC` """
import logging
import os
from pathlib import Path
from typing import Union
from subprocess import Popen, PIPE, STDOUT
from .helper import _check_if_files_exists


class MSC:
    """
    wrapper around the `msc` binary
    """

    BINARY_PATH = "deps/MeasureSuite/bin/msc"

    def __init__(self, files: Union[list[str], list[Path]]):
        """
        :param files:
        """
        self.__supported_file_types = [".asm", ".s"]
        self.__error = False

        if not os.path.exists(MSC.BINARY_PATH):
            self.__error = True
            logging.error("msc binary not found")
            return

        if len(files) < 1:
            self.__error = True
            logging.error("please pass at least a single file to the class")
            return

        _, files = _check_if_files_exists(files, self.__supported_file_types)
        self.files = files

    def execute(self,):
        """
        Internal function. Do call it. Call `run` instead
        :return:
        """
        if self.__error:
            logging.error("error available")
            return False, ""

        cmd = [MSC.BINARY_PATH] + self.files
        for c in cmd:
            assert isinstance(c, str)

        logging.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
                  text=True, encoding="utf-8")
        p.wait()
        assert p.stdout

        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                .replace("\\n'", "")
                .lstrip() for a in data]

        if p.returncode != 0:
            logging.error("Error: MSC: couldn't execute: %s %s", " ".join(cmd), data)
            return False, data

        print(data)
        return True, data

    def run(self):
        """simple helper around execute"""
        return self.execute()

    def __version__(self):
        """
        returns the version.
        """
        return "1.0.0"
