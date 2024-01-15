import logging
import os
from pathlib import Path
from typing import Union
from subprocess import Popen, PIPE, STDOUT


class Wrapper_MS:
    """
    wrapper around the `ms` binary
    """

    BINARY_PATH = "deps/MeasureSuite/ms"
    def __init__(self, file: Union[str, Path]):
        """
        """
        self.file = file
        if type(file) == Path:
            self.file = file.absolute()
    
    def execute(self):
        """
        execute a ms command 
        """

    def __version__(self):
        """
        """
        pass

