
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


US = 0x1F
RS = 0x1E
STX = 0x02


HEADER_GROUP = 0x10

header_group = {
    "operation": HEADER_GROUP | 0x01,
    "serial_id": HEADER_GROUP | 0x02,
    "domain": HEADER_GROUP | 0x03,
    "class": HEADER_GROUP | 0x04,
}
header_group_ = {
    HEADER_GROUP | 0x01 : "operation",
    HEADER_GROUP | 0x02 : "serial_id", 
    HEADER_GROUP | 0x03: "domain",
    HEADER_GROUP | 0x04: "class",
}

PROPERTY_GROUP = 0x020

METADATA_GROUP = 0x020

property_group = {
    "bus_voltage": 0x01,
    "shunt_voltage":  0x02,
    "load_current":  0x03,
}

property_group_ = {
    0x01: "bus_voltage",
    0x02: "shunt_voltage",
    0x03: "load_current",
    0x04: "level",
}

operation_tokens = {
    "READY": 0x01,
    "DATAREQ": 0x02,
    "DATA": 0x03,
    "DATAACK": 0x04,
    "NODEINTROREQ": 0x05,
    "NODEINTRO": 0x06,
    "NODEINTROACK": 0x07,
}


operation_tokens_ = {
    0x01: "READY",
    0x02: "DATAREQ",
    0x03: "DATA",
    0x04: "DATAACK",
    0x05: "NODEINTROREQ",
    0x06: "NODEINTRO",
    0x07: "NODEINTROACK",
}

