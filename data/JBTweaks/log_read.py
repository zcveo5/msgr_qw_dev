import sys
from typing import TextIO


class StdoutReader:
    def __init__(self, file=TextIO):
        self.file = file
        self.__StdoutReader_buffer__ = []

    def write(self, s, /):
        self.__StdoutReader_buffer__.append(s)
        sys.__stdout__.write(s)

    def read(self, n=-1, /):
        return ''.join(self.__StdoutReader_buffer__)



if '__HasCompatibilityTweak__' in globals():
    print('# __HasCompatibilityTweak__ #')
    print('# Replacing sys.stdout #')
    sys.stdout = StdoutReader()
    try:
        load_lbl.place_forget()
    except NameError:
        pass
    print('# sys.stdout replaced! Enjoy #\n\n\nIF YOU USING A LEGACY JAILBREAK MODE, PRESS "work=True" BEFORE CLOSING SERVER SELECT MENU\n\n')
else:
    print('# In Non-legacy mode, log_read is not needed #')