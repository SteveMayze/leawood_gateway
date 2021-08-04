
from leawood.domain.messages import Data, DataAck, IntroAck, NodeIntroReq, Ready, DataReq
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
    ready = Ready('ABCD', '00001', None)
    assert ready.serial_id == 'ABCD'
    assert ready.addr64bit == '00001'
    assert ready.payload == None

    ready = Data('ABCD', '00001', {"bus_voltage": "5.0"})
    assert ready.serial_id == 'ABCD'
    assert ready.addr64bit == '00001'
    assert ready.payload == {"bus_voltage": "5.0"}


def test_receive_message(repository, modem, message_bus, gateway, modem_message_builder):
    payload = {
        'operation': 'DATA',
        'serial_id': '0102030405060708',
        'bus_voltage': 10.5
    }
    rcv_message = modem_message_builder.create_modem_message('00001', payload)
    modem.receive_message(rcv_message)

    # Existing node
    # Push the message to the MQTT queue
    ## TODO - 01.08.21 - This is passing and should not be!
    expected = Data('0102030405060708', '00001', {"bus_voltage": 10.5})
    message = gateway.message_bus.pop()
    assert message == expected
    assert message.payload == expected.payload


def test_receive_ready_message_from_a_known_node(gateway, sensor, modem_message_builder):
    gateway.repository.repository_cache[sensor.addr64bit] = sensor
    payload = {
        'operation': 'READY',
        'serial_id': sensor.serial_id,
    }
    message = modem_message_builder.create_modem_message( sensor.addr64bit , payload)
    gateway.modem.receive_message(message)
    wait_for_empty_queue(gateway.message_bus, True)

    # The hub receives a READY message from a field device
    # This will result in a 'DATA_REQ' being sent out to
    # the sensor.

    message = DataReq(sensor.serial_id, sensor.addr64bit, None)
    assert gateway.modem.spy[sensor.addr64bit] == message


def test_receive_ready_message_from_an_unknown_node(gateway, sensor, modem_message_builder):
    payload = {'operation': 'READY', 'serial_id': sensor.serial_id}
    message = modem_message_builder.create_modem_message( sensor.addr64bit , payload)
    gateway.modem.receive_message(message)
    wait_for_empty_queue(gateway.message_bus, True)

    # The hub receives a READY message from an unknown field device
    # This will result in a 'DATAINTRO' being sent out to
    # the sensor to introduce itself.

    message = NodeIntroReq(sensor.serial_id, sensor.addr64bit, None)
    assert gateway.modem.spy[sensor.addr64bit] == message



def test_receive_data_message(gateway, sensor, modem_message_builder):

    gateway.repository.repository_cache[sensor.addr64bit] = sensor

    payload = {'operation': 'DATA', 'serial_id': sensor.serial_id, 'bus_voltage': 10.5}
    rcv_message = modem_message_builder.create_modem_message(sensor.addr64bit , payload)
    gateway.modem.receive_message(rcv_message)
    wait_for_empty_queue(gateway.message_bus, True)

    # The hub receives a DATA message from a field device
    # This will result in a 'DATA_ACK' being sent out to
    # the sensor.

    # message = modem_message_builder.create_modem_message( sensor.addr64bit ,f'operation=DATAACK\nserial_id={sensor.serial_id}')
    message = DataAck(sensor.serial_id, sensor.addr64bit, None)
    assert gateway.modem.spy[sensor.addr64bit] == message
    # Further to that, the gateway will publish the message
    # to the message bus to be picked up later by 
    # a listener the then post this using R£ST to the DB.
    rcv_message = Data(sensor.serial_id, sensor.addr64bit, {"bus_voltage": "10.5"})
    assert gateway.repository.spy['_post_sensor_data'] == rcv_message


def test_receive_intro_message(gateway, sensor, modem_message_builder):

    gateway.repository.repository_cache[sensor.addr64bit] = sensor
    payload = {
        'operation': 'NODEINTRO', 
        'serial_id': sensor.serial_id, 
        'domain': 'power', 
        'class': 'sensor', 
        'p1': 'bus_voltage',
        'p2': 'shunt_voltage',
        'p3': 'load_current'
        }
    rcv_message = modem_message_builder.create_modem_message(sensor.addr64bit, payload)
    gateway.modem.receive_message(rcv_message)
    wait_for_empty_queue(gateway.message_bus, True)

    # The hub receives a DATA message from a field device
    # This will result in a 'DATA_ACK' being sent out to
    # the sensor.

    message = IntroAck(sensor.serial_id, sensor.addr64bit, None)
    assert gateway.modem.spy[sensor.addr64bit] == message

    # Further to that, the gateway will publish the message
    # to the repository

    assert gateway.repository.spy['_add_node'].addr64bit == sensor.addr64bit
    assert gateway.repository.repository_cache[sensor.addr64bit].addr64bit == sensor.addr64bit
    

