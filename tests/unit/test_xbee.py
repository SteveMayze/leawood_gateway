

from leawood.adapters import xbee
from leawood.domain.messages import Data, NodeIntro, Telegram
from leawood.domain import messages, token

def test_create_message_from_data():
    payload = {
        'operation': 'DATA', 
        'serial_id': '0a0b0c0d0e0f10',
        'bus_voltage': 10.5
    }
    message = messages.create_message_from_data('0102030405060708', payload)
    assert message != None
    assert message.operation == "DATA"
    assert message.addr64bit == "0102030405060708"
    assert len(message.payload) == 1
    assert message.payload['bus_voltage'] == 10.5

    assert isinstance(message, Data)
    

def test_create_message_from_nodeintro():
    payload_dict = {
        'domain': 'power',
        'class': 'sensor',
        'p1': 'bus_voltage',
        'p2': 'shunt_voltage',
        'p3': 'load_current',
    }
    telegram = Telegram('0a0b0c0d0e0f10', 'NODEINTRO', payload_dict)
    payload = messages.transform_telegram_to_bytearray(telegram)
    message = messages.create_message_from_data('010203040506070809', payload)
    assert message != None
    assert message.operation == "NODEINTRO"
    assert message.addr64bit == "010203040506070809"
    assert len(message.payload) == 2
    assert message.payload['p1'] == 'bus_voltage'

    assert isinstance(message, NodeIntro)
    
def test_create_telegram_from_message_data():
    modem = None
    payload = """
    [header]
    operation=DATA
    serial_id=ABCD
    [date]
    bus_voltage=10.5
    load_current=3.8
    """
    message = messages.create_message_from_data('ABCD', payload)
    telegram = xbee.create_telegram_from_message(modem, message)
    # tx = [
    #     HEADER_GROUP, 
    #     OPERATION, operation_tokens['DATA'], RS, 
    #     DATA_GROUP,
    #     data_tokens['bus_voltage'], RS,
    #     data_tokens['load_current'], RS,

    #     ]

    # expected = bytearray(tx).hex()
    # assert  expected == telegram.as_bytearray().hex()