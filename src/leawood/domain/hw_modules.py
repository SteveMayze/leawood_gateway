from leawood.services.messagebus import MessageBus
from leawood.domain.model import Message, Data, Ready, DataReq, DataAck
import abc
import logging 

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

    def __init__(self,  message_bus: MessageBus, modem: Modem):
        self.message_bus = message_bus
        self.modem = modem
        self.nodes = []
        modem.register_receive_callback(self._message_received_callback)
        message_bus.register_message_callback(self._event_received_callback)

    def send_message(self, message: Message):
        logger.info(f'sending message {message}')
        self.modem.send_message(message)

    # Recevies a message from a modem and pushes this directly
    # to the message bus to minimise the time spent.
    def _message_received_callback(self, message: Message):
        logger.info(f'received message {message}')
        self.message_bus.push(message)

    # An asynchronous call back that will andle the messages
    # from the modem
    def _event_received_callback(self, message: Message):
        logger.info(f'received event: {message}')
        if message.operation == Ready.operation:
            logger.info('Operation READY, sending DATA_REQ')
            message = DataReq(message.addr64bit, None)
            self.send_message(message)
        elif message.operation == Data.operation:
            logger.info('Operation DATA, sending DATA_ACK')
            ## Post the data to the repository

            ## call on a REST service layer to post the
            ## message

            message = DataAck(message.addr64bit,None)
            self.modem.send_message(message)
