

from dataclasses import dataclass
from typing import Final


class Message:
    pass

@dataclass
class Ready(Message):
    addr64bit: str
    payload: str
    operation: Final = 'READY'


@dataclass
class DataReq(Message):
    addr64bit: str
    payload: str
    operation: Final = 'DATAREQ'

@dataclass
class Data(Message):
    addr64bit: str
    payload: str
    operation: Final = 'DATA'


@dataclass
class DataAck(Message):
    addr64bit: str
    payload: str
    operation: Final = 'DATAACK'

@dataclass
class NodeIntroReq(Message):
    addr64bit: str
    payload: str
    operation: Final = 'NODEINTROREQ'

@dataclass
class NodeIntro(Message):
    addr64bit: str
    payload: str
    operation: Final = 'NODEINTRO'

@dataclass
class IntroAck(Message):
    addr64bit: str
    payload: str
    operation: Final = 'NODEINTROACK'
