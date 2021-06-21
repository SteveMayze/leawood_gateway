from leawood.services.messagebus import MessageBus
from leawood.domain.model import Message, Data, Ready, DataReq, DataAck
import abc
import logging 

logger = logging.getLogger(__name__)




def handle_ready(message: Message):
    logger.info('Operation READY, sending DATA_REQ')
    newMessage = DataReq( message.modem, message.addr64bit, None)
    message.modem.send_message(newMessage)

def handle_data(message: Message):
    logger.info('Operation DATA, sending DATA_ACK')
    ## Post the data to the repository

    ## call on a REST service layer to post the
    ## message

    newMessage = DataAck( message.modem, message.addr64bit,None)
    message.modem.send_message(newMessage)

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
        message_bus.register_message_handlers(MESSAGE_HANDLERS)

    def send_message(self, message: Message):
        logger.info(f'sending message {message}')
        self.modem.send_message(message)

    # Recevies a message from a modem and pushes this directly
    # to the message bus to minimise the time spent.
    def _message_received_callback(self, message: Message):
        logger.info(f'received message {message}')
        self.message_bus.push(message)

MESSAGE_HANDLERS={
    Ready: handle_ready,
    Data: handle_data

}