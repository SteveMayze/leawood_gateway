
"""

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

    mdp <property> Becomes a group name specific for a particular
    property. [mdp bus_voltage] defines the metadata specific for
    the bus_voltage property. This assumes that these definitions 
    are not yet defined in the application.
    In the new model, it is assumed that the definitions are pre
    defined and standard so the bus_voltage metadata is can be 
    already assumed. This means that the metadata model itself, 
    just needs to connect the properties to the node.

    [header]
    operation=NODEINTRO
    serial_id=ABCD
    domain=power
    class=sensor
    [properties]
    bus_voltage_v
    load_current_a

    HEADER_GROUP operation <operation> serial_id <serial_id>              domain <domain> class <class> RS
          10        11         06         12     xx xx xx xx xx xx xx xx     13      xx      14     xx 
    PROPERTY_GROUP  bus_voltage_v shunt_voltage_v load_current_ma
          20             01             01               01

    20 Bytes

    In this case the name is no longer provided by the devices. This 
    would be added later by the user from within the applications. The
    property names are suffixed with the unit and mulitplier to 
    differentiate between similar properties with different multipliers.

    [header]
    operation=DATA
    serial_id=ABCD
    [data]
    bus_voltage_v=10.5
    load_current_a=3.6

    HEADER_GROUP operation <operation> serial_id <serial_id> 
        01           01        03        01          01
    DATA_GROUP <property> value ... RS
        01          01      04  ... 01

    7 + 5xn bytes
    3 properties = 7 + 5x3 = 22 bytes.
"""

import logging
import struct
from typing import TypedDict


logger = logging.getLogger(__name__)

US = 0x1F
RS = 0x1E
STX = 0x02


HEADER_GROUP = 0x10
OPERATION_GROUP = 0x20
PROPERTY_GROUP = 0x30
METADATA_DOMAIN_GROUP = 0x40
METADATA_CLASS_GROUP = 0x50

telegram_token = {

    "operation": HEADER_GROUP | 0x01,
    "serial_id": HEADER_GROUP | 0x02,
    "domain": HEADER_GROUP | 0x03,
    "class": HEADER_GROUP | 0x04,

    "p": PROPERTY_GROUP | 0x00,
    "bus_voltage": PROPERTY_GROUP | 0x01,
    "shunt_voltage":  PROPERTY_GROUP | 0x02,
    "load_current":  PROPERTY_GROUP | 0x03,

    "READY": OPERATION_GROUP | 0x01,
    "DATAREQ": OPERATION_GROUP | 0x02,
    "DATA": OPERATION_GROUP | 0x03,
    "DATAACK": OPERATION_GROUP | 0x04,
    "NODEINTROREQ": OPERATION_GROUP | 0x05,
    "NODEINTRO": OPERATION_GROUP | 0x06,
    "NODEINTROACK": OPERATION_GROUP | 0x07,

    'power': METADATA_DOMAIN_GROUP | 0x01,
    'capacity': METADATA_DOMAIN_GROUP | 0x02,
    'rate': METADATA_DOMAIN_GROUP | 0x03,
    
    'sensor': METADATA_CLASS_GROUP | 0x01,
    'actuator': METADATA_CLASS_GROUP | 0x01,
}

token_telegram = {}
for name, token in telegram_token.items():
    token_telegram[token] = name



def handle_data_message(telegram: TypedDict):
    props = bytearray()
    for p in telegram.items():
        logger.info(f'Tokenising {p}')
        props.append(telegram_token[p[0]])
        props.extend(struct.pack('f', p[1]))
    return props

def handle_nodeintro_message(telegram: TypedDict):
    props = bytearray()
    for p, label in telegram.items():
        logger.info(f'Tokenising {p}: {label}')
        props.append(telegram_token['p'])
        props.append(telegram_token[label])
    return props



def tokenise(operation: str, serial_id: str, payload: TypedDict):
    """
    Parses the Telegram type and builds a bytearray of the elements
    so that this will be a reduced form for transmission.
    """
    logger.info(f'telegram operation {operation}, seria_id {serial_id} payload {payload}')
    # Each type of Telegram ie message will have specific content. it would be
    # nice to be able to create the various formats in a simple way.
    # https://docs.python.org/3.9/library/ctypes.html#ctypes.c_uint
    datastream = bytearray()
    datastream.append(telegram_token['operation'])
    datastream.append(telegram_token[operation])
    datastream.append(telegram_token['serial_id'])
    datastream.extend(bytearray.fromhex(serial_id))

    properties = None
    if 'DATA' == operation:
        properties = handle_data_message(payload)
    if 'NODEINTRO' == operation: 
        datastream.append(telegram_token['domain'])
        datastream.append(telegram_token[payload.pop('domain')])
        datastream.append(telegram_token['class'])
        datastream.append(telegram_token[payload.pop('class')])
        properties = handle_nodeintro_message(payload)

    if properties:
        datastream.extend(properties)
    return datastream


def detokenise(datastream: bytearray) -> TypedDict:
    """
    Rehydrates a Telegrm from a byte array of tokens.
    """
    logger.info(f'detokenise: tokens {datastream.hex()}')
    payload_data = {}
    logger.info("detokenise: Getting the operation")
    token_0 = datastream[0:1][0]
    operation = None
    logger.info(f"detokenise: token_0 (operation): {token_0}")

    if token_0 == telegram_token['operation']:
        payload_data['operation'] = token_telegram[datastream[1:2][0]]
        logger.info(f"detokenise: operation: {payload_data['operation']}")
    token_0 = datastream[2:3][0]
    logger.info(f"detokenise: token_0 (serial_id): {token_0}")

    if token_0 == telegram_token['serial_id']:
        payload_data['serial_id'] = datastream[3:11].hex()
        logger.info(f"detokenise: serial_id: {payload_data['serial_id']}")

    idx = 1
    data = datastream[11:]
    logger.info(f"detokenise: data: {data}")
    if payload_data['operation'] == 'NODEINTRO':
        prop, val = (data[0:1], data[1:2]) ## domain
        payload_data[token_telegram[prop[0]]] = token_telegram[val[0]]

        prop, val = (data[2:3], data[3:4]) ## class
        payload_data[token_telegram[prop[0]]] = token_telegram[val[0]]
        data = data[4:]

    while len(data) > 0:
        if payload_data['operation'] == 'DATA':
            prop, val = (data[0:1], data[1:5])
            payload_data[token_telegram[prop[0]]] = struct.unpack('f', val)[0]
            data = data[5:]

        if payload_data['operation'] == 'NODEINTRO':
            prop, val = (data[0:1], data[1:2])
            payload_data[f'p{idx}'] = token_telegram[val[0]]
            idx += 1
            data = data[2:]
            
    logger.info(f'detokenise: returning parsed tokens: {datastream}')

    return payload_data
