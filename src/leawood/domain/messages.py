

from dataclasses import dataclass
from typing import TypedDict
from collections import namedtuple
from leawood.domain import token
import logging
import struct

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

def handle_data_message(telegram: TypedDict):
    props = bytearray()
    for p in telegram.items():
        logger.info(f'Tokenising {p}')
        props.append(token.property_group[p[0]])
        props.extend(struct.pack('f', p[1]))
    return props

def handle_nodeintro_message(telegram: TypedDict):
    return None



def tokenise(telegram: Telegram):
    """
    Parses the Telegram type and builds a bytearray of the elements
    so that this will be a reduced form for transmission.
    """
    logger.info(f'telegram {telegram}')
    # Each type of Telegram ie message will have specific content. it would be
    # nice to be able to create the various formats in a simple way.
    # https://docs.python.org/3.9/library/ctypes.html#ctypes.c_uint
    datastream = bytearray()
    datastream.append(token.header_group['operation'])
    datastream.append(token.operation_tokens[telegram.operation])
    datastream.append(token.header_group['serial_id'])
    datastream.extend(bytearray.fromhex(telegram.serial_id))

    properties = None
    if 'DATA' == telegram.operation:
        properties = handle_data_message(telegram.payload)
    if 'NODEINTRO' == telegram.operation: 
        properties = handle_nodeintro_message(telegram.payload)

    if properties:
        datastream.extend(properties)
    return datastream


def detokenise(datastream: bytearray) -> TypedDict:
    """
    Rehydrates a Telegrm from a byte array of tokens.
    """
    logger.info(f'tokens {datastream.hex()}')
    payload_data = {}
    token_0 = datastream[0:1][0]
    operation = None
    if token_0 == token.header_group['operation']:
        payload_data['operation'] = token.operation_tokens_[datastream[1:2][0]]
    token_0 = datastream[2:3][0]
    if token_0 == token.header_group['serial_id']:
        payload_data['serial_id'] = datastream[3:11].hex()

    idx = 1
    data = datastream[11:]
    while len(data) > 0:
        if payload_data['operation'] == 'DATA':
            prop, val = (data[0:1], data[1:6])
            payload_data[token.property_group_[prop[0]]] = struct.unpack('f', val)[0]

        if payload_data['operation'] == 'NODEINTRO':
            prop, val = (data[0:1], data[1,2])
            payload_data[f'p{idx}'] = token.property_group_[prop[0]]
            idx += 1
        data = data[6:]
    return payload_data


def create_message_from_data(addr64bit: str, data: bytearray) -> Message:
    """
    The payload is a byte array of the mandatory (header) properties
    and the optional properties to support the operaiton.
    """
    payload_dict = detokenise(data)
    message = create_message(payload_dict.pop('operation'), payload_dict.pop('serial_id'), addr64bit, payload_dict)
    return message    

def transform_telegram_to_bytearray(telegram: Telegram) -> bytearray:
    """
    Converts the dict payload into a stream of bytes
    """
    return tokenise(telegram)
