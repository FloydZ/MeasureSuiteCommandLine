#!/usr/bin/env python3
""" test """

import logging
import os
from pathlib import Path
from typing import Union
from subprocess import Popen, PIPE, STDOUT


class Msc:
    """
    wrapper around the `msc` binary
    """

    BINARY_PATH = "./deps/MeasureSuite/bin/msc"
    def __init__(self, files: Union[list[str], list[Path]]):
        """
        """
        for f in files:
            ff = f
            if isinstance(f, Path):
                ff = f.absolute()

            assert isinstance(ff, str)
            if not os.path.isfile(ff):
                logging.error("not a file: %s", ff)
                return

        self.files = files
        self.execute(files)

    def execute(self, command: Union[list[str], list[Path]]):
        """
        Internal function. Do call it. Call `run` instead

        :param command: can be either a single file or a list of files
        :return:

        """
        assert isinstance(command, list)
        for i in range(len(command)):
            if isinstance(command[i], Path):
                command[i] = command[i].abspath()

        cmd = [self.BINARY_PATH] + command
        for c in cmd:
            assert isinstance(c, str)

        logging.debug(cmd)
        print(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
                  text=True, encoding="utf-8")
        p.wait()
        assert p.stdout

        print(p.returncode)
        if p.returncode != 0:
            logging.error("Error: MSC: couldnt execute: %s", " ".join(cmd))
            return

        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]
        print(data)

    def __version__(self):
        """
        returns the version.
        """
        return "1.0.0"
