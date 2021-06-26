from leawood.domain.hw_modules import Modem
from leawood.domain.model import Message

class XBeeModem(Modem):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def send_message(self, message: Message):
        pass

    def register_receive_callback(self, callback):
        pass
    
    def receive_message(self, message: Message):
        pass
