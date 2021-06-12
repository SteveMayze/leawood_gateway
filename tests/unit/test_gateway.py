
from leawood.domain.model import Message
from leawood.domain.hw_modules import Gateway, Modem
from leawood.services.messagebus import MessageBus
from leawood.config import Config

import pytest

class FakeModem(Modem):
    def __init__(self):
        self.spy = {}
        self._receive_message_callback = None

    def send_message(self):
        pass

    def register_receive_callback(self, callback):
        self._receive_message_callback  = callback

    def receive_message(self, message):
       self._receive_message_callback(message)
    

@pytest.fixture
def config():
    args = ["--serial-port", "COM1", "--baud", "9600", "--sleeptime", "0"]
    return Config(args)


@pytest.fixture
def modem() -> Modem:
    return  FakeModem()

def test_receive_message(config, modem):

    message = Message('00001', '{"bus-voltage": 10.5}')
    message_bus = MessageBus()
    gateway = Gateway(message_bus, modem)

    modem.receive_message(message)

    # Existing node
    # Push the message to the MQTT queue

    assert gateway.message_bus.pop() == message

    


