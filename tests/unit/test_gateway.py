
## import gateway
from gateway.domain.model import Message, Gateway
from gateway.services.message_bus import MessageBus

def test_recevie_message():

    message = Message('address')
    message_bus = MessageBus()
    gateway = Gateway(message_bus)
    gateway.message_received_callback(message)

    # Existing node
    # Push the message to the MQTT queue

    assert gateway.message_bus.pop() == message

    

