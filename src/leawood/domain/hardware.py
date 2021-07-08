

from typing import Any, Callable
from leawood.services.messagebus import MessageBus
from leawood.services.repository import Repository
from leawood.domain.messages import IntroAck, Message, Data, NodeIntroReq, Ready, DataReq, DataAck, NodeIntro
from leawood.domain import messages
from leawood.domain.model import Node
import abc
import logging 


logger = logging.getLogger(__name__)

class Modem(abc.ABC):
    """
    The abstract class for a Modem type. This defines the primary interface
    that a modem should support to operate within this system.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def send_message(self, message: Message):
        """
        Sends a message via the implemented modem to a device
        that is addressed within the message.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def register_receive_callback(self, callback: Callable):
        """
        Registers a callback function that is called when a message
        has been received on the implemented Modem type.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def receive_message(self, message: Any):
        """
        Called when a modem type implementation receives a message.
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def open(self):
        """
        Opens the connection to the modem.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        """
        Closes the connection to the modem and releases the resource.
        """
        raise NotImplementedError



class Sensor(Node):

    def __init__(self, message_bus: MessageBus = None, modem: Modem = None):
        self.message_bus = message_bus
        self.modem = modem
        self._addr64bit = None
        self.device_id = None
        self.node_class = None
        self.name = None
        self.serial_id = None
        self.description = None
        self.location = None
        self.domain = None
        if message_bus != None:
            message_bus.register_message_handlers(self.get_handlers())
        if modem != None:
            modem.register_receive_callback(self.receive_message_callback)



    ## This could eventuall pass over to be a serial number
    ## since the address might not always
    def addr64bit(self):
        return self._addr64bit

    def addr64bit(self, value):
        self._addr64bit = value

    def send_message(self, message: Message):
        logger.info(f'Sensor sending message {message}')
        self.modem.send_message(message)

    def receive_message_callback(self, message):
        logger.info(f'Sensor recevied message {message.operation}, {message.payload}')
        self.message_bus.push(message)

    def handle_DataReq(self, message: Message):
        logger.info('Handling the DATAREQ event')
        pass

    def get_handlers(self):
        MESSAGE_HANDLERS = {
            DataReq: self.handle_DataReq,
        }
        return MESSAGE_HANDLERS

    def open(self):
        self.modem.open()

    def close(self):
        self.modem.close()        


class Gateway(Node):

    def __init__(self,  message_bus: MessageBus, repository: Repository, modem: Modem):
        self.message_bus = message_bus
        self.modem = modem
        self.repository = repository

        modem.register_receive_callback(self.receive_message_callback)
        message_bus.register_message_handlers(self.get_handlers())


    def send_message(self, message: Message):
        logger.info(f'Gateway sending message {message}')
        self.modem.send_message(message)

    # Recevies a message from a modem and pushes this directly
    # to the message bus to minimise the time spent.
    def receive_message_callback(self, message: Message):
        logger.info(f'Gateway recevied message {message.operation}, {message.payload}')
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
            newMessage = NodeIntroReq( message.addr64bit, None)
            self.modem.send_message(newMessage)


    def handle_data(self, message: Message):
        ## Post the data to the repository
        logger.info('Operation DATA, posting to the respository')

        self.repository.post_sensor_data(message)

        logger.info('Operation DATA, sending DATA_ACK')
        newMessage = DataAck( message.addr64bit,None)
        self.modem.send_message(newMessage)

    def handle_new_node(self, message: Message):
        ## TODO - The type of node needs to be qualified so that the
        ##        corrent object is created.
        node = Sensor(None, None)
        node.addr64bit = message.addr64bit
        self.repository.add_node(node)
        ackMessage = IntroAck(message.addr64bit, None)
        self.modem.send_message(ackMessage)

    def get_handlers(self):
        MESSAGE_HANDLERS = {
            Ready: self.handle_ready,
            Data: self.handle_data,
            NodeIntro: self.handle_new_node
        }
        return MESSAGE_HANDLERS


    def open(self):
        self.modem.open()

    def close(self):
        self.modem.close()        

