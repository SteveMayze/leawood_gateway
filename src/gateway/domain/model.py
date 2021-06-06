
from gateway.services.message_bus import MessageBus
from dataclasses import dataclass

@dataclass(frozen=True)
class Message():
    address: str


class Gateway():
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus

    @property
    def message_bus(self):
        return self._message_bus

    @message_bus.setter
    def message_bus(self, value):
        self._message_bus = value

    def message_received_callback(self, message: Message):
        self.message_bus = [message]