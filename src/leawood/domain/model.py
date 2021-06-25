
from dataclasses import dataclass
from typing import Final
import abc

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
class NodeIntro(Message):
    addr64bit: str
    payload: str
    operation: Final = 'NODEINTRO'


class Node(abc.ABC):


    @property
    def addr64bit(self):
        raise NotImplementedError

    @addr64bit.setter
    def addr64bit(self, value):
        raise NotImplementedError

    @abc.abstractmethod
    def send_message(self):
        raise NotImplementedError

    @abc.abstractmethod
    def receive_message_callback(self, message):
        raise NotImplementedError
        self.message_bus.push(message)
