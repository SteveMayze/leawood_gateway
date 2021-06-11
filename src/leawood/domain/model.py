
from dataclasses import dataclass

@dataclass(frozen=True)
class Message():
    address: str
