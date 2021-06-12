from leawood.services.messagebus import MessageBus
import abc

class Modem(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def send_message(self):
        raise NotImplementedError

    @abc.abstractmethod
    def register_receive_callback(self, callback):
        raise NotImplementedError

    @abc.abstractmethod
    def receive_message(self, message):
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

    def send_message(self):
        self.modem.send_message()

    def _message_received_callback(self, message):
        self.message_bus.push(message)
