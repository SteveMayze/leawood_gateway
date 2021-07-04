from leawood.domain.hardware import Modem
from leawood.domain.messages import Message
from leawood.domain import messages
import logging
from  digi.xbee import devices


logger = logging.getLogger(__name__)

class XBeeModem(Modem):
    def __init__(self, config):
        super().__init__()
        self.config = config
        com = self.config.config_data['serial-port']
        baud = int(self.config.config_data['serial-baud'])
        logger.info(f'Creating a coordinator with a connection to {com} at {baud}')
        self.xbee = devices.XBeeDevice(com, baud)

        self._receive_callback = None

    def send_message(self, message: Message):
        self.open()
        logger.info(f'Creating the remote device at {message.addr64bit}')
        remote_device = devices.RemoteXBeeDevice(self.xbee, devices.XBee64BitAddress.from_hex_string(message.addr64bit))
        logger.info(f'Sending from {self.xbee.get_64bit_addr()} to {message.addr64bit}')
        ## TODO - Need to add the operation to the payload
        self.xbee.send_data(remote_device, str(message.payload))

    def register_receive_callback(self, callback):
        self.open()
        self._receive_message = callback
        self.xbee.add_data_received_callback(self.receive_message)
    
    def receive_message(self, xbee_message):
        address = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data.decode('utf8')
        logger.info(f'XBee received message {data}')
        ## TODO - The payload must container the operation.
        message = messages.create_message(operation, address, data)
        self._receive_message(message)


    def open(self):
        if( self.xbee is not None and self.xbee.is_open() == False):
            self.xbee.open()

    """
    Closes the connection to the coordinator.
    """
    def close(self):
        if( self.xbee is not None and self.xbee.is_open()):
            self.xbee.close()
