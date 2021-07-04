
from leawood.domain.messages import IntroAck, Data, NodeIntroReq, Ready, DataReq, DataAck, NodeIntro
import logging 
import time

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



def test_message():
    ready = Ready('00001', '{"param": "value"}')
    assert ready.addr64bit == '00001'
    assert ready.payload == '{"param": "value"}'


def test_receive_message(repository, modem, message_bus, gateway):
    # message_bus = LocalMessageBus()
    # gateway = Gateway(message_bus, repository, modem)
    message = Data('00001', '{"bus-voltage": 10.5}')

    modem.receive_message(message)

    # Existing node
    # Push the message to the MQTT queue
    assert gateway.message_bus.pop() == message


def test_receive_ready_message_from_a_known_node(gateway, sensor):
    gateway.repository.repository_cache[sensor.addr64bit] = sensor

    message = Ready(sensor.addr64bit, None)
    gateway.modem.receive_message(message)
    wait_for_empty_queue(gateway.message_bus, True)

    # The hub receives a READY message from a field device
    # This will result in a 'DATA_REQ' being sent out to
    # the sensor.

    message = DataReq(sensor.addr64bit, None)
    assert gateway.modem.spy[sensor.addr64bit] == message


def test_receive_ready_message_from_an_unknown_node(gateway, sensor):

        message = Ready(sensor.addr64bit, None)
        gateway.modem.receive_message(message)
        wait_for_empty_queue(gateway.message_bus, True)

        # The hub receives a READY message from an unknown field device
        # This will result in a 'DATAINTRO' being sent out to
        # the sensor to introduce itself.

        message = NodeIntroReq(sensor.addr64bit, None)
        assert gateway.modem.spy[sensor.addr64bit] == message



def test_receive_data_message(gateway, sensor):

    gateway.repository.repository_cache[sensor.addr64bit] = sensor

    payload = '{"bus-voltage": 10.5}'
    rcv_message = Data(sensor.addr64bit, payload)
    gateway.modem.receive_message(rcv_message)
    wait_for_empty_queue(gateway.message_bus, True)

    # The hub receives a DATA message from a field device
    # This will result in a 'DATA_ACK' being sent out to
    # the sensor.

    message = DataAck(sensor.addr64bit,None)
    assert gateway.modem.spy[sensor.addr64bit] == message
    # Further to that, the gateway will publish the message
    # to the MQTT message bus to be picked up later by 
    # a listener the then post this using R£ST to the DB.

    assert gateway.repository.spy['_post_sensor_data'] == rcv_message


def test_receive_intro_message(gateway, sensor):

    gateway.repository.repository_cache[sensor.addr64bit] = sensor

    payload = '{"domain": "power", "class": "sensor", "name":"solar", "metadata":[{"bus-voltage":{"unit":"volts", "multiplier":1.0}}, {"load-current":{"unit":"amperes", "multiplier":0.001}}]}'
    rcv_message = NodeIntro(sensor.addr64bit, payload)
    gateway.modem.receive_message(rcv_message)
    wait_for_empty_queue(gateway.message_bus, True)

    # The hub receives a DATA message from a field device
    # This will result in a 'DATA_ACK' being sent out to
    # the sensor.

    message = IntroAck(sensor.addr64bit, None)
    assert gateway.modem.spy[sensor.addr64bit] == message

    # Further to that, the gateway will publish the message
    # to the repository

    assert gateway.repository.spy['_add_node'].addr64bit == sensor.addr64bit
    assert gateway.repository.repository_cache[sensor.addr64bit].addr64bit == sensor.addr64bit


