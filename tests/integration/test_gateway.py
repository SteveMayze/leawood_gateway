
from leawood.adapters.rest import Rest
from leawood.adapters.xbee import XBeeModem
from leawood.config import Config
import pytest

import logging

from leawood.domain.messages import Ready
from leawood.domain.hardware import Gateway, Sensor
from leawood.services.messagebus import LocalMessageBus
from leawood.services import messagebus 
import time
import uuid
import json

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


class TestGateway:

    def test_repository_get_node(self, config):
        respository = Rest(config)
        node = respository.get_node('0013A200415D58CB')
        assert node != None
        assert node.serial_id == '0013A200415D58CB'
        assert node.description == 'The power monitor  on the mobile chicken coop'


    def test_repository_add_node(self, config):
        random_addr = str(uuid.uuid1())
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
        assert node.serial_id == random_addr
        assert node.description == 'A device generated via integration tests'


    def test_gateway_operation(self, config, sensor):
    
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
            sensor.send_message( Ready('0013A20041AE49D4', None))
            
            # Verify the Data request.
            logger.info('Waiting 10 seconds...')
            time.sleep(10)


            messagebus.shutdown(message_bus)
            wait_for_runnning_state(message_bus, False)
        finally:
            gateway.close()
            sensor.close()