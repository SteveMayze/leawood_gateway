
from leawood.adapters.rest import Rest
from leawood.adapters.xbee import XBeeModem
from leawood.config import Config
import pytest

import logging

from leawood.domain.hardware import Gateway
from leawood.services.messagebus import LocalMessageBus
from leawood.services import messagebus 
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


class TestGateway:

    def test_repository_get_node(self, config):
        respository = Rest(config)
        node = respository.get_node('0013A200415D58CB')
        assert node != None
        assert node.serial_id == '0013A200415D58CB'
        assert node.description == 'The power monitor  on the mobile chicken coop'


    def test_gateway_operation(self, config):

        ## TODO - A better story is required to determin how and
        ##        when the modem is opened and closed.
        modem = XBeeModem(config)
        message_bus = LocalMessageBus()
        repository = Rest(config)

        gateway = Gateway(message_bus, repository, modem)

        messagebus.activate(message_bus)
        wait_for_runnning_state(message_bus, True)

        messagebus.shutdown(message_bus)
        wait_for_runnning_state(message_bus, False)
        modem.close()
