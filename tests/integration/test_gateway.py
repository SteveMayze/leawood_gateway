
from leawood.adapters.rest import Rest
from leawood.adapters.xbee import XBeeModem
from leawood.config import Config
import pytest

import logging

from leawood.domain.messages import Data, DataAck, Ready, DataReq
from leawood.domain.hardware import Gateway, Sensor
from leawood.services.messagebus import LocalMessageBus, MessageBus
from leawood.services import messagebus 
import time
import uuid
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MAX_WAIT = 2

def wait_for_message(message_bus: MessageBus):
    start_time = time.time()
    while True:
        try:
            return message_bus.pop()
        except (AssertionError) as error:
            if time.time() - start_time > MAX_WAIT: 
                raise error 
            time.sleep( 0.5)   

def wait_for_empty_queue(message_bus: MessageBus, state: bool):
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


class TestGateway:
    """
    tests/integration/test_gateway.py::TestGateway::test_gateway_operation
    """
    def test_repository_get_node(self, config):
        respository = Rest(config)
        node = respository.get_node('0013A200415D58CB')
        assert node != None
        assert node.serial_id == '0013A200415D58CB'
        assert node.description == 'The power monitor  on the mobile chicken coop'


    def test_repository_add_node(self, config):
        random_addr = uuid.uuid1().hex[:16]
        respository = Rest(config)
        node = Sensor()
        node.addr64bit = random_addr
        node.domain = 'POWER'
        node.node_class = 'SENSOR'
        node.serial_id = random_addr
        node.name = f'TEST GENERATED DEVICE {random_addr}'
        node.description = 'A device generated via integration tests'
        node = respository.add_node(node)
        assert node != None
        assert node.serial_id == random_addr.upper()
        assert node.description == 'A device generated via integration tests'


    def test_gateway_data_operation(self, config, sensor):
        """"
        Tests the operation from the point of view of a node seding the READY
        operation and the response from the gateway to say that it is free
        to send i.e. DATAREQ and then the response of the DATA and then the final 
        DATAACK.
        """
    
        """
        RED   0013A20041AE49D4
        GREEN 0013A200415D58CB
        """

        ## TODO - A better story is required to determin how and
        ##        when the modem is opened and closed.
        modem = XBeeModem(config)
        message_bus = LocalMessageBus()
        repository = Rest(config)

        try:
            gateway = Gateway(message_bus, repository, modem)

            messagebus.activate(message_bus)
            wait_for_runnning_state(message_bus, True)

            # Sensor to send READY.
            logger.info('Sending Ready to the gateway node')
            sensor.send_message( Ready('0013A200415D58CB', '0013A20041AE49D4', None))
            time.sleep(5)

            # Verify the Data request.
            message = wait_for_message(sensor.message_bus)
            assert message != None
            assert isinstance(message, DataReq)
            # payload = """
            # bus_voltage=10.5
            # load_current=3.2
            # """

            # The payload can only be 73 bytes. So this type of payload is not 
            # going to work. the value labels need to be tokenised. 
            # This poses a problem for the metadata to define the information
            # from a senser node.
            rand_voltage = random.randrange(105, 165)/10
            rand_current = random.randrange(1,2500)/1000
            payload = {
                "bus_voltage": rand_voltage,
                "load_current": rand_current
            }
            
            sensor.send_message(Data('0013A200415D58CB', '0013A20041AE49D4', payload))
            time.sleep(7)

            message = wait_for_message(sensor.message_bus)
            assert isinstance(message, DataAck)

            ## The message bus is not running for the sensor, this
            ## then needs to be querired manually i.e. like a spy
            ## for the purpose of the test.

            ## Get message from the sensor message bus
            ## Execite the message bus callback
            ## This is where we need to inject some values
            ## to be sent to the database.

            

            messagebus.shutdown(message_bus)
            wait_for_runnning_state(message_bus, False)
        finally:
            gateway.close()
            sensor.close()


    def test_sensor_send(self, config, sensor):
        """
        A rough test to send a message without verification. This is used in conjunction
        with the XCTU tool to verify the physical messages sent. 
        """

        try:

            # Sensor to send READY.
            logger.info('Sending Ready to the gateway node')
            sensor.send_message( Ready('0013A200415D58CB', '0013A20041AE49D4', None))
            time.sleep(5)

            payload = {
                "bus_voltage": 10.5,
                "shunt_voltage": 0.85,
                "load_current": 3.2
            }
            logger.info('Sending Ready to the gateway node')
            sensor.send_message( Data('0013A200415D58CB', '0013A20041AE49D4', payload))

        finally:
            sensor.close()            