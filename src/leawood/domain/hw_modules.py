from leawood.services.messagebus import MessageBus
from leawood.services.repository import Repository
from leawood.domain.model import Message, Data, Ready, DataReq, DataAck, NodeIntro, Node
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



class Sensor(Node):

    def __init__(self, message_bus: MessageBus, modem: Modem):
        self.message_bus = message_bus
        self.modem = modem

    ## This could eventuall pass over to be a serial number
    ## since the address might not always
    def addr64bit(self):
        return self.modem.addr64bit

    def addr64bit(self, value):
        self.modem.addr64bit = value

    def send_message(self):
        self.modem.send_message()

    def receive_message_callback(self, message):
        self.message_bus.push(message)


class Gateway():

    def __init__(self,  message_bus: MessageBus, repository: Repository, modem: Modem):
        self.message_bus = message_bus
        self.modem = modem
        self.repository = repository

        modem.register_receive_callback(self._message_received_callback)
        message_bus.register_message_handlers(self.get_handlers())


    def send_message(self, message: Message):
        logger.info(f'sending message {message}')
        self.modem.send_message(message)

    # Recevies a message from a modem and pushes this directly
    # to the message bus to minimise the time spent.
    def _message_received_callback(self, message: Message):
        logger.info(f'received message {message}')
        self.message_bus.push(message)



    def handle_ready(self, message: Message):
        logger.info('Operation READY, sending DATA_REQ')
        ## First of all determine if this is from a registered node
        node = self.repository.get_node(message.addr64bit)
        if node != None:
            ## If so, then send a request for data.
            logger.info(f'The node {node} has requested further instruction')
            newMessage = DataReq( message.addr64bit, None)
            self.modem.send_message(newMessage)
        else:
            ## Else, send a request for introduction
            logger.info(f'The node {node} has requested further instruction')
            newMessage = NodeIntro( message.addr64bit, None)
            self.modem.send_message(newMessage)


    def handle_data(self, message: Message):
        logger.info('Operation DATA, sending DATA_ACK')
        ## Post the data to the repository

        ## call on a REST service layer to post the
        ## message

        newMessage = DataAck( message.addr64bit,None)
        self.modem.send_message(newMessage)

    def get_handlers(self):
        MESSAGE_HANDLERS = {
            Ready: self.handle_ready,
            Data: self.handle_data
        }
        return MESSAGE_HANDLERS