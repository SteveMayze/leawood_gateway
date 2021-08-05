

from dataclasses import dataclass
from typing import TypedDict
from  leawood.adapters import token
import logging

logger = logging.getLogger(__name__)

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
    def __init__(self, operation:str , serial_id:str, addr64bit:str, payload) -> None:
        self.operation = operation
        self.serial_id = serial_id
        self.addr64bit = addr64bit
        self.payload = payload

@dataclass
class Ready(Message):

    def __init__(self, serial_id, addr64bit, payload) -> None:
        super().__init__('READY', serial_id, addr64bit, payload)

@dataclass
class DataReq(Message):
    def __init__(self, serial_id, addr64bit, payload) -> None:
        super().__init__('DATAREQ', serial_id, addr64bit, payload)

@dataclass
class Data(Message):
    def __init__(self, serial_id, addr64bit, payload) -> None:
        super().__init__('DATA', serial_id, addr64bit, payload)


@dataclass
class DataAck(Message):
    def __init__(self, serial_id, addr64bit, payload) -> None:
        super().__init__('DATAACK', serial_id, addr64bit, payload)

@dataclass
class NodeIntroReq(Message):
    def __init__(self, serial_id, addr64bit, payload) -> None:
        super().__init__('NODEINTROREQ', serial_id, addr64bit, payload)

@dataclass
class NodeIntro(Message):
    def __init__(self, serial_id, addr64bit, payload) -> None:
        super().__init__('NODEINTRO', serial_id, addr64bit, payload)

@dataclass
class IntroAck(Message):
    def __init__(self, serial_id, addr64bit, payload) -> None:
        super().__init__('NODEINTROACK', serial_id, addr64bit, payload)


def create_message(operation, serial_id, addr64bit, payload) -> Message:
    return {
        'READY': Ready( serial_id, addr64bit, payload),
        'DATAREQ': DataReq( serial_id, addr64bit, payload),
        'DATA': Data( serial_id, addr64bit, payload),
        'DATAACK': DataAck( serial_id ,addr64bit, payload),
        'NODEINTROREQ': NodeIntroReq( serial_id, addr64bit, payload),
        'NODEINTRO': NodeIntro( serial_id, addr64bit, payload),
        'NODEINTROACK': IntroAck( serial_id, addr64bit, payload),
    }[operation]


def create_message_from_data(addr64bit: str, data: bytearray) -> Message:
    """
    The payload is a byte array of the mandatory (header) properties
    and the optional properties to support the operaiton.
    """
    payload_dict = token.detokenise(data)
    message = create_message(payload_dict.pop('operation'), payload_dict.pop('serial_id'), addr64bit, payload_dict)
    return message    

def transform_telegram_to_bytearray(telegram: Telegram) -> bytearray:
    """
    Converts the dict payload into a stream of bytes
    """
    return token.tokenise(telegram.operation, telegram.serial_id, telegram.payload)
