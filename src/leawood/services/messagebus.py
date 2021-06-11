import queue
from leawood.domain.model import Message

class MessageBus:
    def __init__(self):
        self.message_queue = queue.Queue()

    @property
    def message_queue(self) -> queue.Queue:
        return self._message_queue

    @message_queue.setter
    def message_queue(self, value: queue.Queue):
        self._message_queue = value


    def push(self, message):
        self.message_queue.put(message)

    def pop(self):
        return self.message_queue.get()

