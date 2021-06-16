import queue
from leawood.domain.model import Message
import time
from threading import Thread
import logging 


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def activate(message_bus):
    logger.info(f'Starting the message bus')
    if message_bus.event_callback == None:
        raise MessageBusError('The event bus must have a callback defined.')
    message_bus.listener_thread = Thread(target=message_bus._listener)
    message_bus.listener_thread.start()

def shutdown(message_bus):
    logger.info(f'Shutting down the message bus')
    message_bus.terminate()
    message_bus.listener_thread.join()


class MessageBusError(Exception):
    def __init__(self, message):
        super().__init__(message)

class MessageBus:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.event_callback = None

    @property
    def message_queue(self) -> queue.Queue:
        return self._message_queue

    @message_queue.setter
    def message_queue(self, value: queue.Queue):
        self._message_queue = value

    def is_running(self):
        return self._running

    def terminate(self):
        self._running = False

    def register_message_callback(self, callback):
        self.event_callback = callback

    def push(self, message):
        self.message_queue.put(message)

    def pop(self):
        try:
            return self.message_queue.get(True, 1)
        except queue.Empty:
            pass

    def empty(self):
        return self.message_queue.empty()


    def _listener(self):
        self._running = True
        while self.is_running():
            item = self.pop()
            if item != None:
                logger.info(f'Calling the callback {self.event_callback}')
                self.event_callback(item)
                self.message_queue.task_done()
