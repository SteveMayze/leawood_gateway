

from dataclasses import dataclass
from typing import Final, TypedDict

@dataclass
class Telegram:
    """
    The telegram represents the data received from the modem unit. This information
    is provided by the seding unit and must contain a serial_id and an operation
    identifier. The payload is optional but, when present, is excpected to be a
    name value pair.
    """
    serial_id: str
    operation: str
    payload: TypedDict

class Message:
    def __init__(self, operation, addr64bit, payload) -> None:
        self.operation = operation
        self.addr64bit = addr64bit
        self.payload = payload

@dataclass
class Ready(Message):

    def __init__(self, addr64bit, payload) -> None:
        super().__init__('READY', addr64bit, payload)

@dataclass
class DataReq(Message):
    def __init__(self, addr64bit, payload) -> None:
        super().__init__('DATAREQ', addr64bit, payload)

@dataclass
class Data(Message):
    def __init__(self, addr64bit, payload) -> None:
        super().__init__('DATA', addr64bit, payload)


@dataclass
class DataAck(Message):
    def __init__(self, addr64bit, payload) -> None:
        super().__init__('DATAACK', addr64bit, payload)

@dataclass
class NodeIntroReq(Message):
    def __init__(self, addr64bit, payload) -> None:
        super().__init__('NODEINTROREQ', addr64bit, payload)

@dataclass
class NodeIntro(Message):
    def __init__(self, addr64bit, payload) -> None:
        super().__init__('NODEINTRO', addr64bit, payload)

@dataclass
class IntroAck(Message):
    def __init__(self, addr64bit, payload) -> None:
        super().__init__('NODEINTROACK', addr64bit, payload)


def create_message(operation, addr64bit, payload) -> Message:
    return {
        'READY': Ready(addr64bit, payload),
        'DATAREQ': DataReq(addr64bit, payload),
        'DATA': Data(addr64bit, payload),
        'DATAACK': DataAck(addr64bit, payload),
        'NODEINTROREQ': NodeIntroReq(addr64bit, payload),
        'NODEINTRO': NodeIntro(addr64bit, payload),
        'NODEINTROACK': IntroAck(addr64bit, payload),
    }[operation]