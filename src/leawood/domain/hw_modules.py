from leawood.services.messagebus import MessageBus
from leawood.domain.model import Message
import abc
import logging 
from typing import Final
from leawood.services import mqtt

logger = logging.getLogger(__name__)

class Modem(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def send_message(self, message: Message):
        raise NotImplementedError

    @abc.abstractmethod
    def register_receive_callback(self, callback):
        raise NotImplementedError

    @abc.abstractmethod
    def receive_message(self, message: Message):
        raise NotImplementedError


class Sensor():
    def __init__(self, message_bus: MessageBus, modem: Modem):
        self.message_bus = message_bus
        self.modem = modem

    def send_message(self):
        self.modem.send_message()

    def receive_message_callback(self, message):
        self.message_bus.push(message)


class Gateway():

    READY: Final = 'READY'
    DATA_REQ: Final = 'DATAREQ'
    DATA: Final = 'DATA'
    DATA_ACK: Final = 'DATAACK'

    def __init__(self,  message_bus: MessageBus, modem: Modem, mqtt: mqtt.MQTT):
        self.message_bus = message_bus
        self.modem = modem
        self.mqtt = mqtt
        self.nodes = []
        modem.register_receive_callback(self._message_received_callback)
        message_bus.register_message_callback(self._event_received_callback)

    def send_message(self, message: Message):
        logger.info(f'sending message {message}')
        self.modem.send_message(message)

    def _message_received_callback(self, message: Message):
        logger.info(f'received message {message}')
        self.message_bus.push(message)

    def _event_received_callback(self, message: Message):
        logger.info(f'received event: {message}')
        if message.operation == Gateway.READY:
            logger.info('Operation READY, sending DATA_REQ')
            message = Message(message.addr64bit, Gateway.DATA_REQ, None)
            self.modem.send_message(message)
        elif message.operation == Gateway.DATA:
            logger.info('Operation DATA, sending DATA_ACK')
            ## Post the data to the MQTT
            mqtt.publish(self.mqtt, message)
            message = Message(message.addr64bit, Gateway.DATA_ACK, None)
            self.modem.send_message(message)
