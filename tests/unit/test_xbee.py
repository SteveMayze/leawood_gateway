

from leawood.adapters import xbee
from leawood.domain.messages import Data, NodeIntro, Ready
from leawood.domain import messages 

def test_create_message_from_data():
    message = messages.create_message_from_data('ABCD', "[header]\nserial_id=ABCD\noperation=DATA\n[data]\nbus_voltage=5.0")
    assert message != None
    assert message.operation == "DATA"
    assert message.addr64bit == "ABCD"
    assert len(message.payload) == 1
    assert message.payload['bus_voltage'] == '5.0'

    assert isinstance(message, Data)
    

def test_create_message_from_nodeintro():
    payload = """
    [header]
    operation=NODEINTRO
    serial_id=ABCD
    domain=power
    class=sensor
    name=solar
    [mdp bus_voltage]
    unit=volts
    symbol=V
    multiplier=1.0
    [mdp load_current]
    unit=amps
    symbol=A
    multiplier=1.0
    """
    message = messages.create_message_from_data('ABCD', payload)
    assert message != None
    assert message.operation == "NODEINTRO"
    assert message.addr64bit == "ABCD"
    assert len(message.payload) == 2
    assert message.payload['bus_voltage']['unit'] == 'volts'
    assert message.payload['load_current']['unit'] == 'amps'

    assert isinstance(message, NodeIntro)
        