

from leawood.adapters import xbee
from leawood.domain.messages import Ready

def test_create_message_from_data():
    message = xbee.create_message_from_data('ABCD', "serial_id=ABCD\noperation=READY\nbus_voltage=5.0")
    assert message != None
    assert message.operation == "READY"
    assert message.addr64bit == "ABCD"
    assert len(message.payload) == 1
    assert message.payload['bus_voltage'] == '5.0'

    assert isinstance(message, Ready)
    