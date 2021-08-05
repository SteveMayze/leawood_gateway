
import abc



class Node(abc.ABC):
    @property
    def addr64bit(self):
        raise NotImplementedError

    @addr64bit.setter
    def addr64bit(self, value):
        raise NotImplementedError

    @property
    def serial_id(self):
        raise NotImplementedError

    @serial_id.setter
    def serial_id(self, value):
        raise NotImplementedError

    @abc.abstractmethod
    def send_message(self):
        raise NotImplementedError

    @abc.abstractmethod
    def receive_message_callback(self, message):
        raise NotImplementedError

    @abc.abstractclassmethod
    def open(self):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError
