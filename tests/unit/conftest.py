from dataclasses import dataclass
from typing import Callable, TypedDict
from leawood.domain.messages import Message
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
    addr64bit:str
    payload: str
    # def __init__(self, addr64bit, payload) -> None:
    #     self.addr64bit = addr64bit
    #     self.payload = payload


class FakeModem(Modem):
    def __init__(self):
        self.spy = {}
        self._receive_message_callback = None

    def send_message(self, message: Message):
        logger.info(f'Send message: {message}')
        assert isinstance(message.addr64bit, str)
        self.spy[message.addr64bit] = message

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
        self.repository_cache[node.addr64bit] = node
    
    def _get_node(self, addr64bit: str) -> Node:
        self.spy['_get_node'] = addr64bit
        if addr64bit in self.repository_cache:
            return self.repository_cache[addr64bit]
        return None

    def _post_sensor_data(self, node: Node, message: Message):
        self.spy['_post_sensor_data'] = message
        pass


class MessageBuilder():
    def create_message(self, addr64bit, payload):
        return FakeMessage(addr64bit, payload)


@pytest.fixture
def message_builder():
 return MessageBuilder()


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
    sensor.serial_id = 'ABCD'
    sensor.addr64bit = "00000001"
    return sensor

