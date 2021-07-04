import queue
from typing import Callable, Dict, Type
from leawood.domain.messages import Message
import time
from threading import Thread
import logging 
import abc

logger = logging.getLogger(__name__)


class MessageBusError(Exception):
    def __init__(self, message):
        super().__init__(message)


class MessageBus(abc.ABC):
    def __init__(self) -> None:
        self.message_handlers = None
        self._running = False

    def is_running(self):
        return self._running

    def terminate(self):
        self._running = False

    def register_message_handlers(self, message_handlers: Dict[Type[Message], Callable]):
        self.message_handlers = message_handlers

    def _listener(self):
        self._running = True
        while self.is_running():
            message = self.pop()
            if message != None:
                event_handler = self.message_handlers[type(message)]
                logger.info(f'Calling the messagse handler {event_handler}')
                event_handler(message)
                self.message_queue.task_done()

    @abc.abstractmethod
    def push(self, message: Message):
        raise NotImplementedError

    @abc.abstractmethod
    def pop(self) -> Message:
        raise NotImplementedError

    @abc.abstractmethod
    def empty(self):
        raise NotImplementedError




class LocalMessageBus(MessageBus):
    def __init__(self):
        super().__init__()
        self.message_queue = queue.Queue()

    @property
    def message_queue(self) -> queue.Queue:
        return self._message_queue

    @message_queue.setter
    def message_queue(self, value: queue.Queue):
        self._message_queue = value


    def push(self, message: Message):
        self.message_queue.put(message)

    def pop(self) -> Message:
        try:
            return self.message_queue.get(True, 1)
        except queue.Empty:
            pass

    def empty(self):
        return self.message_queue.empty()


class MQTTMessageBus(MessageBus):
    def __init__(self):
        super().__init__()
        self.message_queue = queue.Queue()





def activate(message_bus: MessageBus):
    logger.info(f'Starting the message bus')
    if message_bus.message_handlers == None:
        raise MessageBusError('The event bus must have a callback defined.')
    message_bus.listener_thread = Thread(target=message_bus._listener)
    message_bus.listener_thread.start()

def shutdown(message_bus: MessageBus):
    logger.info(f'Shutting down the message bus')
    message_bus.terminate()
    message_bus.listener_thread.join()

