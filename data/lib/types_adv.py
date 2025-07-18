"""Types"""
from typing import Protocol


class SupportRead(Protocol):
    """Class supports 'read' method"""
    def read(self, size: int = -1) -> str: ...


class SupportWrite(Protocol):
    """Class supports 'write' method"""
    def write(self, s: str, /) -> int: ...


class SupportsConfig(Protocol):
    """Class supports 'config' method"""
    def config(self,) -> int: ...