
from dataclasses import dataclass

@dataclass(frozen=True)
class Message():
    addr64bit: str
    operation: str
    payload: str
