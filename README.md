# Base Station
This module represents the code for implementing a base-station. This is a node of the network that will act as a coordinator to the modules in range. This will maintain a list of the near-by nodes and request data from them from time to time.

# Requirements
Python 3.9+

# Creating a local environment

```shell
python3.9 -m venv .venv
.venv\Scripts\activate
```

```shell
pip intall -r requirements.txt
pip install -e src
```

It may be necessary to reinstall the digi-xbee to pick up the serial package.
```shell
pip install --upgrade --force-reinstall digi-xbee
```

## Starting the gate way

```python -m leawood.gateway -v```

```shell
python -m leawood.gateway -h
usage: gateway.py [-h] [-c config_file] [-v] [-u user_name] [-w password] [-r rest] [-C certpath] [-a cacert] [-l clientcrt] [-k clientkey] [-m mqttserver] [-p mqttport]
                  [-f file] [-s serial-port] [-b baud] [-S sleeptime]

Start and stop the gateway

optional arguments:
  -h, --help            show this help message and exit
  -c config_file, --config config_file
                        The configuration file containing the common arguments
  -v, --verbose         Enable debug mode
  -u user_name, --username user_name
                        The username for the REST service
  -w password, --password password
                        The password for the REST service
  -r rest, --rest rest  The base ReST endpoint
  -C certpath, --certpath certpath
                        The path to the certificates
  -a cacert, --cacert cacert
                        The name of the CA certificate
  -l clientcrt, --clientcrt clientcrt
                        The name of the client certificate
  -k clientkey, --clientkey clientkey
                        The name of the client key file
  -m mqttserver, --mqttserver mqttserver
                        The IP address of the MQTT server
  -p mqttport, --mqttport mqttport
                        The port for the MQTT sever
  -f file, --file file  The name of the payload file
  -s serial-port, --serial-port serial-port
                        The serial port for the XBee module
  -b baud, --baud baud  The baud rate for the XBee module
  -S sleeptime, --sleeptime sleeptime
                        The sleep time when waiting to request new information
```

## Running the tests

```
pytest
```

Running the tests with logging
```
pytest -v -s --log-cli-level INFO
```
## Generating the Documentation
 
 ```
 pdoc -o .\docs .\src\leawood
```

# Use Cases

The purpose of the Hub is to act as a gateway between the radio units (currently XBee) and the application (i.e. database). Once the process starts up it will launch three other independent threads 

1. Message handler to control the messages too and from the radio units.
2. MQTT subscriber to react to messages from the radio units and post the data to the application via REST.
3. MQTT subscriber to receive messages from the application and post to the message handler.

The purpose of these independent threads is to ensure that the thread that monitors the radio unit has sole access to the serial port.

# Message Handler
The message handler is the thread that opens the connection to the serial port that is connected to the radio unit. To avoid clashes, there is only one thread that will have access to the port. It is also important that when receiving or sending messages to and from the radio unit that the connection is as short as possible. There fore where possible a message bus will be used. At this stage, MQTT is the choice for the message bus, though it might eventuate that this is excessive.

The message handler will be running in an infinite loop. Its time will be divided between

1. Receving messages from the field
2. Checking the application message queue for further instructions
3. Pausing in an idle state

In the idle state, the message handler will be waiting for messages from a node. These messages will be in the form of a wake up call to indicate that they are awake and either have information or are requesting further instruction. The message handler can then check the queue for any application specific messages or can indicate to the node to proceed with its telegram.

There needs to be a management check in the list of associated nodes to see when the last time a node was in contact. If a threshold is exceeded, then the application is informed of a potential field problem.

## Node Available
When the gateway receives a Node Available message, this idicates that a sensor node has woken and is available to receive commands. This can be new configuration information from the application or it can be a request tha the node should provide its current readings.

The node available message will need to be checked against a list of known nodes so that the gateway can deal with a newly added node.

## New Node
If the node is not currently registered in the local list, then a request to the application will be made. If this is a new node, then the new entries will be made and the node added to the local list. It could well be that this node has moved from one gateway to another. In this case no new node is needed to be registered buy the allocated gateway should change.

## Node Removed

## Node Reconnected

## Node Configuration

# MQTT Subscriber - Posting messages to the application
This MQTT subscriber will receive messages from the Message Handler and package them into a compatible format to be received by the application. Performing the work in this manner means that the message handler does not have to spend time and can simply receive its message from the radio unit and push it to the queue.

# MQTT Subscriber - Receiving messages from the application
The MQTT subscriber for receiving message from the application will take these messages and prepare them for transmission. These will then be posted onto a local queue that the message handler is monitoring and will take them from the queue and transmit them.

# Node Metadata
A node, for all intents and purposes, is a sensor. This will take readings and transmit them to the nearest hub that they are connected to. Each sensor node will be tracking one or more measurements and these measurements will have their units and multipliers. The problem to solve is getting this information to the user interface in a way in which there is minimal effort for the user and programmer to set up the various parameters. To solve this the thought is that when a new node is introduced to a hub, then the hub should ask for what data it can expect. The telegram it receives back should have each data element the sensor will supply. Each element will include its label, SI unit and multiplier. This information is then sent to the application and the node along with its expected data elements are registered into the database.


# TODO
1. The Rest module is not being _injected_. It is not healthy that this is being created down in the Subscriber code.
2. Error handling needs to be consolidated and improved
3. The naming of the class hierarchy is no longer appropriate and should be refactored.
4. There needs to be a protocol devised for the various use cases.
5. The _coordinator_ needs to react and control the protocol.
6. Finalise the payload structure

