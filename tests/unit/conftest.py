from dataclasses import dataclass
from typing import Callable, TypedDict
from leawood.domain.messages import Message, Telegram
from leawood.domain import messages
from leawood.domain.model import Node
from leawood.domain.hardware import Gateway, Modem, Sensor
from leawood.services.messagebus import LocalMessageBus
from leawood.services import messagebus
from leawood.config import Config
import logging 
import pytest
import time
from leawood.services.repository import Repository

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



MAX_WAIT = 1

def wait_for_empty_queue(message_bus, state):
    start_time = time.time()
    while True:
        try:
            assert message_bus.empty() == state
            return
        except (AssertionError) as error:
            if time.time() - start_time > MAX_WAIT: 
                raise error 
            time.sleep( 0.5)   

def wait_for_runnning_state(worker, state):
    start_time = time.time()
    while True:
        try:
            assert worker.is_running() == state
            return
        except (AssertionError) as error:
            if time.time() - start_time > MAX_WAIT: 
                raise error 
            time.sleep( 0.5)    



@dataclass
class FakeMessage():
    """
    This represents the raw message sent and received by the Modem.
    The payload should contain at least the serial_id and operation
    plus an optional data or metdata section for the additional 
    information to support the operation.
    The modem implementation should transform this into a Message 
    object.
    """
    addr64bit:str
    payload: bytearray


class FakeModem(Modem):
    def __init__(self):
        self.spy = {}
        self._receive_message_callback = None

    def send_message(self, message: Message):
        logger.info(f'Send message: {message}')
        assert isinstance(message.serial_id, str)
        self.spy[message.serial_id] = message

    def register_receive_callback(self, callback: Callable):
        self._receive_message_callback  = callback

    def receive_message(self, in_message: FakeMessage):
        logger.info(f'Received message: {in_message}')
        message = messages.create_message_from_data(in_message.addr64bit, in_message.payload)
        self._receive_message_callback(message)
    
    def open(self):
        pass

    def close(self):
        pass


class FakeRepository(Repository):
    def __init__(self) -> None:
        super().__init__()
        self.repository_cache = {}
        self.spy = {}

    def _add_node(self, node: Node):
        self.spy['_add_node'] = node
        self.repository_cache[node.serial_id] = node
    
    def _get_node(self, serial_id: str) -> Node:
        self.spy['_get_node'] = serial_id
        if serial_id in self.repository_cache:
            return self.repository_cache[serial_id]
        return None

    def _post_sensor_data(self, node: Node, message: Message):
        self.spy['_post_sensor_data'] = message
        pass


class ModemMessageBuilder():
    def create_modem_message(self, addr64bit: str, payload: TypedDict):
        # TODO - convert the data into a bytearray!
        telegram = Telegram(payload.pop('serial_id'), payload.pop('operation'), payload)
        data = messages.transform_telegram_to_bytearray(telegram)
        return FakeMessage(addr64bit, data)


@pytest.fixture
def modem_message_builder():
 return ModemMessageBuilder()


@pytest.fixture
def config():
    args = ["--serial-port", "COM1", "--baud", "9600", "--sleeptime", "0"]
    return Config(args)


@pytest.fixture(scope='function')
def modem() -> Modem:
    modem = FakeModem()
    yield modem
    modem.spy = {}

@pytest.fixture(scope='function')
def repository() -> Repository:
    repository = FakeRepository()
    yield repository
    repository.repository_cache = {}
    repository.spy = {}

@pytest.fixture(scope='function')
def message_bus():
    message_bus = LocalMessageBus()
    return message_bus


@pytest.fixture(scope='function')
def gateway(message_bus, repository, modem):
    gateway = Gateway(message_bus, repository, modem)
    messagebus.activate(message_bus)
    logger.info(f'Waiting for the message bus to start')
    wait_for_runnning_state(message_bus, True)
    yield gateway
    logger.info(f'Waiting for the message bus to shut down')
    messagebus.shutdown(message_bus)
    wait_for_runnning_state(message_bus, False)



@pytest.fixture(scope='function')
def sensor():
    sensor = Sensor(None, None)
    sensor.serial_id = '0102030405060708'
    sensor.addr64bit = '090a0b0c0d0e0f10'
    return sensor

