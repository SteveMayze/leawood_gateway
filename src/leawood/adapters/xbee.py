from collections import namedtuple
from typing import Callable

from digi.xbee.models.message import XBeeMessage
from leawood.domain.hardware import Modem
from leawood.domain.messages import Data, DataAck, DataReq, IntroAck, Message, NodeIntro, NodeIntroReq, Ready, Telegram
from leawood.domain import messages
from leawood.config import Config
import logging
from  digi.xbee import devices


logger = logging.getLogger(__name__)

class XBeeTelegram(Telegram):
    pass

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
        self.xbee.send_data(remote_device, str(xbee_telegram))

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
        data = xbee_message.data.decode('utf8')
        logger.info(f'XBee received message {data}')
        message = create_message_from_data(str(address), data)
        self._receive_message(message)


    def open(self):
        """
        Opens the connection to the XBee module.
        """
        if( self.xbee is not None and self.xbee.is_open() == False):
            self.xbee.open()

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
    data = message.payload
    telegram_data = {}

    while data:
        property, nl, data = data.partition('\n')
        if property != None:
            name, assign, value = property.partition('=')
            value = value.replace('\\=','=')
            telegram_data[name]=value
        else:
            break
    ## TODO - This is OK to create an object from a dictionary but this
    ##        is still not what is required. The serial_id and operation
    ##        will come through but the payload will then be object properties.
    ##        They need to be bundled.
    telegram = namedtuple("XbeeTelegram", telegram_data.keys())(*telegram_data.values())
    return telegram


def create_message_from_data(addr64bit: str, data: str) -> Message:
    """
    The payload is assumed to be a name value pair.
    Delimited with an equals and a new line between parameters.
    The equals should be escaped with the \\=
    """
    payload_dict = {}

    while data:
        property, nl, data = data.partition('\n')
        if property != None:
            name, assign, value = property.partition('=')
            value = value.replace('\\=','=')
            payload_dict[name]=value
        else:
            break
    ## TODO - This is OK to create an object from a dictionary but this
    ##        is still not what is required. The serial_id and operation
    ##        will come through but the payload will then be object properties.
    ##        They need to be bundled.
    message_tuple = namedtuple(payload_dict["operation"], payload_dict.keys())(*payload_dict.values())
    payload_dict.pop('operation')
    payload_dict.pop('serial_id')
    message = messages.create_message(message_tuple.operation, message_tuple.serial_id, addr64bit, payload_dict)

    return message