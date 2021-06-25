
from leawood.domain.model import Message, Data, Ready, DataReq, DataAck, Node
from leawood.domain.hw_modules import Gateway, Modem, Sensor
from leawood.services import repository
from leawood.services.messagebus import LocalMessageBus
from leawood.services import messagebus
from leawood.config import Config
import logging 
import pytest
import time

from leawood.services.repository import Repository



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
    

class FakeRepository(Repository):
    repository_cache = {}

    def _add_node(self, node: Node):
        self.repository_cache[node.addr64bit] = node
    
    def _get_node(self, addr64bit: str) -> Node:
        if addr64bit in self.repository_cache:
            return self.repository_cache[addr64bit]
        return None

    def _post_sensor_data(self, message: Message):
        pass

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
    repository = FakeRepository()
    message_bus = LocalMessageBus()
    gateway = Gateway(message_bus, repository, modem)
    message = Data('00001', '{"bus-voltage": 10.5}')

    modem.receive_message(message)

    # Existing node
    # Push the message to the MQTT queue
    assert gateway.message_bus.pop() == message


def test_receive_ready_message_from_a_known_node(config, modem):

        repository = FakeRepository()

        message_bus = LocalMessageBus()
        known_node = Sensor(message_bus, modem)
        gateway = Gateway(message_bus, repository, modem)
        known_node.addr64bit = '00001'
        repository.repository_cache[known_node.addr64bit] = known_node

        messagebus.activate(message_bus)
        logger.info(f'Waiting for the message bus to start')
        wait_for_runnning_state(message_bus, True)

        message = Ready('00001', None)
        modem.receive_message(message)
        wait_for_empty_queue(message_bus, True)

        # The hub receives a READY message from a field device
        # This will result in a 'DATA_REQ' being sent out to
        # the sensor.

        message = DataReq('00001', None)
        assert modem.spy['00001'] == message

        logger.info(f'Waiting for the message bus to shut down')
        messagebus.shutdown(message_bus)
        wait_for_runnning_state(message_bus, False)


def test_receive_data_message(config, modem):

        repository = FakeRepository()
        message_bus = LocalMessageBus()
        gateway = Gateway(message_bus, repository, modem)

        messagebus.activate(message_bus)
        logger.info(f'Waiting for the message bus to start')
        wait_for_runnning_state(message_bus, True)

        payload = '{"bus-voltage": 10.5}'
        rcv_message = Data('00001', payload)
        modem.receive_message(rcv_message)
        wait_for_empty_queue(message_bus, True)

        # The hub receives a DATA message from a field device
        # This will result in a 'DATA_ACK' being sent out to
        # the sensor.

        message = DataAck('00001',None)
        assert modem.spy['00001'] == message


        logger.info(f'Waiting for the message bus to shut down')
        messagebus.shutdown(message_bus)
        wait_for_runnning_state(message_bus, False)

        # Further to that, the gateway will publish the message
        # to the MQTT message bus to be picked up later by 
        # a listener the then post this using R£ST to the DB.

        ## assert mqtt_bus.spy['PUBLISH'] == rcv_message


