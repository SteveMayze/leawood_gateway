
from leawood.domain.model import Message
from leawood.domain.hw_modules import Gateway, Modem
from leawood.services.messagebus import MessageBus
from leawood.services import messagebus
from leawood.config import Config
import logging 
import pytest
import time


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FakeModem(Modem):
    def __init__(self):
        self.spy = {}
        self._receive_message_callback = None

    def send_message(self, message: Message):
        logger.info(f'Send message: {message}')
        self.spy[message.addr64bit] = message

    def register_receive_callback(self, callback):
        self._receive_message_callback  = callback

    def receive_message(self, message: Message):
        logger.info(f'Received message: {message}')
        self._receive_message_callback(message)
    

@pytest.fixture
def config():
    args = ["--serial-port", "COM1", "--baud", "9600", "--sleeptime", "0"]
    return Config(args)


@pytest.fixture
def modem() -> Modem:
    return  FakeModem()

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

def test_receive_message(config, modem):
    message = Message('00001', 'DATA', '{"bus-voltage": 10.5}')
    message_bus = MessageBus()
    gateway = Gateway(message_bus, modem)

    modem.receive_message(message)

    # Existing node
    # Push the message to the MQTT queue
    assert gateway.message_bus.pop() == message


def test_receive_ready_message(config, modem):

        message_bus = MessageBus()
        gateway = Gateway(message_bus, modem)

        messagebus.activate(message_bus)
        logger.info(f'Waiting for the message bus to start')
        wait_for_runnning_state(message_bus, True)

        message = Message('00001', Gateway.READY, None)
        modem.receive_message(message)
        wait_for_empty_queue(message_bus, True)

        # The hub receives a READY message from a field device
        # This will result in a 'DATA_REQ' being sent out to
        # the sensor.

        message = Message('00001', Gateway.DATA_REQ, None)
        logger.info(f'Spy -> {modem.spy}')
        ## time.sleep( 5 )
        assert modem.spy['00001'] == message

        logger.info(f'Waiting for the message bus to shut down')
        messagebus.shutdown(message_bus)
        wait_for_runnning_state(message_bus, False)




