# Base Station
This module represents the code for implementing a base-station. This is a node of the network that will act as a coordinator to the modules in range. This will maintain a list of the near-by nodes and request data from them from time to time.

# Requirements
Python 3.9+

https://raspberrytips.com/install-latest-python-raspberry-pi/
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

## Starting the gateway

The gateway will start and stay running in that thread. It can be terminated via a keyboard interrupt
or by using the stop command from another terminal session.

```python -m leawood.gateway -v```

```shell
python -m leawood -h
usage: __main__.py [-h] [-c config_file] [-v] [-u user_name] [-w password]
                   [-l logfile] [-r rest] [-s serial-port] [-b baud]
                   [-S sleeptime]
                   {start,stop} ...

Start and stop the gateway

positional arguments:
  {start,stop}

optional arguments:
  -h, --help            show this help message and exit
  -c config_file, --config config_file
                        The configuration file containing the common arguments
  -v, --verbose         Enable debug mode
  -u user_name, --username user_name
                        The username for the REST service
  -w password, --password password
                        The password for the REST service
  -l logfile, --logfile logfile
                        The name of the log file
  -r rest, --rest rest  The base ReST endpoint
  -s serial-port, --serial-port serial-port
                        The serial port for the XBee module
  -b baud, --baud baud  The baud rate for the XBee module
  -S sleeptime, --sleeptime sleeptime
                        The sleep time when waiting to request new information

$
```

## Running the tests
The tests use pytest. When ran normally, there will be an internal version of a gateway created
and started. The tests can be ran against an indepentant gateway i.e. a staging gateway by setting
an envrionment variable to indicate to the tests no to user the internal version.

The STAGING_GATEWAY defines the addres the pseudo sensor should use ( this will be factored out in 
another iteration of changes). The STAGED flag indicates whether to create the internal gateway service
or to use another hosted elsewhere.

Linux
```shell
export STAGING_GATEWAY=<GATEWAY ADDRESS>
export STAGED=(True|False)
```

Powershell
```powershell
$Env:STAGING_GATEWAY = "<GATEWAY ADDRESS>"
$Env:export STAGED = ("True"|"False")
```

```
pytest
```

Running the tests with logging
```
pytest -v -s --log-cli-level INFO
```

## Deployment
Deployment uses Fabric3 and the fabfile.py located in the deploy_tools directory. This should take care of creating the 
environment for the gateway to run. There are issues with Raspberry Pi Zero where some dependant libraries had to be 
installed and the Python 3.9 code compiled against these libraries.

```shell
wget https:// www.python. org/ftp/python/3.9.5/Python-3.9.6.tgz
tar -zxvf Python-3.9.6.tgz
sudo apt-get install libffi-dev
sudo apt-get install build-essential checkinstall 
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
cd Python-3.9.6
sudo ./configure --enable-optimizations
sudo make altinstall

# Make Python3.9 default
cd /usr/bin
sudo rm python
sudo ln -s /usr/local/bin/python3.9 python
python --version
```
Once the Python 3.9 is installed and made default, the fabric module can be used to then deploy the gateway
to the Raspberry Pi.

```shell
cd deploy_tools
fab deploy:host=<HOST CONNECTION>
```

## Generating the Documentation
 
 ```
 pdoc -o .\docs .\src\leawood
```

# Use Cases

The purpose of the Hub is to act as a gateway between the radio units (currently XBee) and the application (i.e. database). Once the process starts up it will launch three other independent threads 

1. Message handler to control the messages too and from the radio units.
2. An internal queue is used to react to messages from the radio units and post the data to the application via REST.
3. An internal queue is used to receive messages from the application and post to the message handler.

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

# Node Metadata
A node, for all intents and purposes, is a sensor. This will take readings and transmit them to the nearest hub that they are connected to. Each sensor node will be tracking one or more measurements and these measurements will have their units and multipliers. The problem to solve is getting this information to the user interface in a way in which there is minimal effort for the user and programmer to set up the various parameters. To solve this the thought is that when a new node is introduced to a hub, then the hub should ask for what data it can expect. The telegram it receives back should have each data element the sensor will supply. Each element will include its label, SI unit and multiplier. This information is then sent to the application and the node along with its expected data elements are registered into the database.


# TODO
1. The Rest module is not being _injected_. It is not healthy that this is being created down in the Subscriber code.
2. Error handling needs to be consolidated and improved
3. The naming of the class hierarchy is no longer appropriate and should be refactored.
4. There needs to be a protocol devised for the various use cases.
5. The _coordinator_ needs to react and control the protocol.
6. Finalise the payload structure

