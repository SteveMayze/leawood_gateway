
from dataclasses import dataclass
from typing import Final

class Message:
    pass

@dataclass
class Ready(Message):
    modem: object
    addr64bit: str
    payload: str
    operation: Final = 'READY'


@dataclass
class DataReq(Message):
    modem: object
    addr64bit: str
    payload: str
    operation: Final = 'DATAREQ'

@dataclass
class Data(Message):
    modem: object
    addr64bit: str
    payload: str
    operation: Final = 'DATA'


@dataclass
class DataAck(Message):
    modem: object
    addr64bit: str
    payload: str
    operation: Final = 'DATAACK'
