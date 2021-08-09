
import logging

from leawood.domain.messages import Data, DataAck, Ready, DataReq
from leawood.services.messagebus import MessageBus
import time
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


class TestGateway:
    """
    tests/integration/test_gateway.py::TestGateway::test_gateway_operation
    """

    def test_gateway_data_operation(self, sensor, gateway):
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

        try:


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

            rand_voltage = round(random.randrange(105, 165)/10, 2)
            rand_current = round(random.randrange(1,2500)/1000, 2)
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

        finally:
            sensor.close()            


    def test_sensor_send(self, sensor, gateway):
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