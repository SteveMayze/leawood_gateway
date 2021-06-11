
from leawood.domain.model import Message
from leawood.domain.hw_modules import Gateway, Modem
from leawood.services.messagebus import MessageBus
from leawood.config import Config

import pytest


@pytest.fixture
def config():
    args = ["--serial-port", "COM1", "--baud", "9600", "--sleeptime", "0"]
    return Config(args)


@pytest.fixture
def modem() -> Modem:
    return 

def test_receive_message(config, modem):

    message = Message('address')
    message_bus = MessageBus()
    gateway = Gateway(message_bus, modem)
    gateway.message_received_callback(message )

    # Existing node
    # Push the message to the MQTT queue

    assert gateway.message_bus.pop() == message

    


