import logging
import os
from pathlib import Path
from typing import Union
from subprocess import Popen, PIPE, STDOUT


class Wrapper_MSC:
    """
    wrapper around the `msc` binary
    """

    BINARY_PATH = "./deps/MeasureSuite/bin/msc"
    def __init__(self, files: Union[list[str], list[Path]]):
        """
        """
        for f in files:
            ff = f
            if type(f) == Path:
                ff = f.absolute()

            assert type(ff) == str
            if not os.path.isfile(ff):
                logging.error("not a file: " + ff)
                return

        self.files = files
        self.__execute(files)

    
    def __execute(self, command: Union[list[str], list[Path]]):
        """
        Internal function. Do call it. Call `run` instead

        :param command: can be either a single file or a list of files
        :return:

        """
        assert type(command) == list
        for i in range(len(command)):
            if type(command[i]) == Path:
                command[i] = command[i].abspath()

        cmd = [self.BINARY_PATH] + command
        for c in cmd:
            assert type(c) == str
        
        logging.debug(cmd)
        print(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True, text=True, encoding="utf-8")
        p.wait()
        assert p.stdout

        print(p.returncode)
        if p.returncode != 0:
            logging.error("Error: MSC: couldnt execute: " + " ".join(cmd))
            return 

        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]
        print(data)

    def __version__(self):
        """
        """
        pass
