

from typing import Callable
from digi.xbee.models.message import XBeeMessage
from leawood.domain.hardware import Modem
from leawood.domain.messages import  Message, Telegram
from leawood.domain import messages
from leawood.config import Config
import logging
from  digi.xbee import devices


logger = logging.getLogger(__name__)



class XBeeTelegram(Telegram):
    """
    The XBeeTelegram represents the message to be written to the XBee modem device. The __repr__
    method is setup to output the payload to be passed down to the modem.
    """
    def __init__(self, message: Message):
       super(XBeeTelegram, self).__init__(message.serial_id.upper(), message.operation, message.payload)

    def as_bytearray(self) -> bytearray:
        telegram = messages.transform_telegram_to_bytearray(self)
        return telegram


class XBeeModem(Modem):
    """
    Provides the XBee implementation of a Modem.
    """

    def __init__(self, config: Config):
        """
        The constructor for the XBeeModem object. This requires a config object
        to provide the correct configuration to be able to make a connection
        to the actual physical XBee modem module.
        """
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
        ##        and to convert this to a XBee format.
        xbee_telegram = create_telegram_from_message(self, message)
        logger.info(f'message {repr(xbee_telegram)}')
        self.xbee.send_data(remote_device, xbee_telegram.as_bytearray())

    def register_receive_callback(self, callback: Callable):
        """
        Registers the fuction to be called when the XBee module recevies a
        message. The message recevied from the XBee module will be of type
        XBeeMessage. This will be converted to Message and bassed to the 
        callback.
        """
        self.open()
        self._receive_message = callback
        self.xbee.add_data_received_callback(self.receive_message)
    
    def receive_message(self, xbee_message: XBeeMessage):
        """
        The handler for the messages recevied by the XBee module. This function
        will parse the content of the XBeeMessage and convert this to a Message
        type and pass this to the callback.
        """
        address = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data
        logger.info(f'XBee received message {data.hex()}')
        message = messages.create_message_from_data(str(address), data)
        self._receive_message(message)


    def open(self):
        """
        Opens the connection to the XBee module.
        """
        if( self.xbee is not None and self.xbee.is_open() == False):
            self.xbee.open()
            self.xbee.set_sync_ops_timeout(10)

    def close(self):
        """
        Closes the connection to the XBee module.
        """
        if( self.xbee is not None and self.xbee.is_open()):
            self.xbee.close()


def create_telegram_from_message(modem: XBeeModem, message: Message) -> XBeeTelegram:
    """
    A message needs to be converted to a XBeeTelegram type. This is the
    payload of the XBeeMessage to go out to the target device. The basic 
    telegram contains a serial_id, an operation and a payload. The payload
    is a name value pair.
    """
   
    telegram = XBeeTelegram(message)
    return telegram

