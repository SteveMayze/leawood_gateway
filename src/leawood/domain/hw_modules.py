from leawood.services.messagebus import MessageBus

class Modem():
    pass

class Sensor():
    def __init__(self, message_bus: MessageBus, modem: Modem):
        self.message_bus = message_bus
        self.modem = modem

class Gateway():
    def __init__(self,  message_bus: MessageBus, modem: Modem):
        self.message_bus = message_bus
        self.modem = modem


    def message_received_callback(self, message):
        self.message_bus.push(message)
