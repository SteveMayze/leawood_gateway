

from dataclasses import dataclass
from typing import Final, TypedDict
from collections import namedtuple
import configparser
import io
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




def __create_message_from_data(addr64bit: str, data: str) -> Message:
    """
    The payload is assumed to be a name value pair.
    Delimited with an equals and a new line between parameters.
    The equals should be escaped with the \\=
    """
    payload_dict = {}

    while data:
        property, nl, data = data.partition('\n')
        if property != None:
            name, assign, value = property.partition('=')
            value = value.replace('\\=','=')
            payload_dict[name]=value
        else:
            break
    ## TODO - This is OK to create an object from a dictionary but this
    ##        is still not what is required. The serial_id and operation
    ##        will come through but the payload will then be object properties.
    ##        They need to be bundled.
   #  message_tuple = namedtuple(payload_dict["operation"], payload_dict.keys())(*payload_dict.values())
    operation = payload_dict.pop('operation')
    serial_id = payload_dict.pop('serial_id')
    message = create_message(operation, serial_id, addr64bit, payload_dict)

    return message    


    
def create_message_from_data(addr64bit: str, data: str) -> Message:
    """
    The payload is in the format of a configuration file.
    """
    payload_buf = io.StringIO(data)
    cfg = configparser.ConfigParser()
    cfg.read_file(payload_buf)

    # operation = payload_dict.pop('operation')
    # serial_id = payload_dict.pop('serial_id')

    header = dict(cfg.items('header'))
    sections = cfg.sections()
    payload_dict = {}
    for section in sections:
        properties = dict(cfg.items(section))
        logger.info(f'section: {section}: properties: {properties}')
        if section.startswith('mdp '):
            md = dict(cfg.items(section))
            section = section.replace('mdp ', '', 1)
            payload_dict[section] = md
        elif section == 'data':
            data = dict(cfg.items(section))
            payload_dict = data


    message = create_message(header['operation'], header['serial_id'], addr64bit, payload_dict)

    return message    
