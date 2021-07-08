

from leawood.adapters import xbee

def test_create_message_from_data():
    message = xbee.create_message_from_data("serial_id=ABCD\noperation=READY")
    assert message != None
    assert message.operation == "READY"
    assert message.serial_id == "ABCD"
    