


class MessageBus:
    def __init__(self):
        self.message_queue = []

    @property
    def message_queue(self):
        return self._message_queue

    @message_queue.setter
    def message_queue(self, value):
        self._message_queue = value

