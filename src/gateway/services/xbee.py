
from  digi.xbee import devices
from digi.xbee.exception import XBeeException
from  leawood.base import AbstractCoordinator
from  leawood.base import AbstractSensor
import time
import json
from threading import Thread

"""
Broadcases a request to locate any neighboring nodes.
"""
def scan_network(coordinator):
    try:
        coordinator._scan_network()
        return "OK"
    except XBeeException:
        return "EXCEPTION"


"""
Cycles through the list of devices and requests from each one if they have any data.
"""
def request_data(coordinator):
    try:
        coordinator._request_data()
        return "OK"
    except XBeeException as e:
        return f"EXCEPTION: {type(e)}, {e.args}, {e}"

"""
Record the error to the home base.
"""
def record_error(coordinator):
    return "OK"


"""
Checks the MQTT queue for any device specific instructions
"""
def check_for_instructions(coordinator):
    return "OK"

"""
Sends an instructional messages to a specific deivces.
"""
def send_instructions(coordinator):
    return "OK"

"""
activates the coordinator and starts the control loop.
"""
def activate(coordinator):
    ## try:
        status = scan_network(coordinator)
        if "OK" != status:
            record_error(coordinator) 

        coordinator.register_listeners(coordinator.data_receive_callback)
        if "OK" != status:
            record_error(coordinator) 
        coordinator.listener_thread = Thread(target=coordinator._listener)
        coordinator.listener_thread.start()

    ## except Exception as e:
    ##    coordinator.log.error(f'Runtime exception {e}')

def send_data(sensor, address, payload):
    try:
        sensor._send_data(address, payload)
        return "OK"
    except XBeeException as e:
        return f"EXCEPTION: {type(e)}, {e.args}, {e}"

def shutdown(coordinator):
    try: 
        coordinator.terminate()
        coordinator.log.debug(f'Waiting for the listener to shutdown')
        coordinator.listener_thread.join()
        coordinator.log.debug(f'The listener has shutdown')
    finally:
        coordinator.close()



"""
The XBee module/classes provides an API wrapper around the XBee Python module
"""
class Coordinator(AbstractCoordinator):


    def __init__(self, config, publisher):
        super(Coordinator, self).__init__(config, publisher, "XBee_Coordinator")
        self._coordinating_device = None
        self._running = False
        self.log.debug('XBee_Coordinator: __init__')
        self._listener_thread = None



    @property
    def coordinating_device(self):
        if ( self._coordinating_device == None):
            com = self.config.config_data['serial-port']
            baud = int(self.config.config_data['serial-baud'])
            self.log.info(f'Creating a coordinator with a connection to {com} at {baud}')
            self.coordinating_device = devices.XBeeDevice(com, baud)
        return self._coordinating_device

    @coordinating_device.setter
    def coordinating_device(self, device):
        self._coordinating_device = device
        self.log.debug(f"Created Coordinating device {self._coordinating_device}")

    @property
    def listener_thread(self):
        return self._listener_thread

    @listener_thread.setter
    def listener_thread(self, value):
        self._listener_thread = value

    def is_running(self):
        return self._running

    def terminate(self):
        self.log.debug(f'Setting the listener flag to false')
        self._running = False

    """
    Broadcases a request to locate any neighboring nodes.
    """
    def _scan_network(self):
        coordinator_device = self.coordinating_device
        self.log.debug(f'Located the coordinator: {coordinator_device}')
        self.open()
        xnet = coordinator_device.get_network()
        xnet.start_discovery_process(deep=True, n_deep_scans=1)
        self.log.debug(f'Discovering the network: {xnet}')
        while xnet.is_discovery_running():
            time.sleep(0.5)

        # Get the list of the nodes in the network.
        nodes = xnet.get_devices()
        self.log.debug(f'Retrieved the nodes {nodes}')

        for node in nodes:
            device = json.loads(f'{{"NI": "{node.get_node_id()}", "PL": "{node.get_power_level()}", "ADDRESS": "{node.get_64bit_addr()}", "ADDR": "{node.get_16bit_addr()}"}}')
            device['device-id'] = 'NOT-SET'
            self._nodes.append(device)

        self.log.debug (f'Network: {self._nodes}')


    def __str__(self):
        return f'Coordinator'


    """
    Cycles through the list of devices and requests from each one if they have any data.
    """
    def _request_data(self):
        coordinator_device = self.coordinating_device
        self.log.debug(f'Located the coordinator: {coordinator_device.get_node_id()}')
        self.open()

        for remote in self.nodes:
            self.log.debug(f'Sending a data request to {remote["ADDRESS"]}')
            remote_device = devices.RemoteXBeeDevice(coordinator_device, devices.XBee64BitAddress.from_hex_string(remote['ADDRESS']))
            self.log.debug(f'Sending a DATA_REQ to {remote_device}')
            ## coordinator_device.send_data(remote_device, 'DATA_REQ')
            ## coordinator_device.send_data_broadcast( 'DATA_REQ')
            coordinator_device.send_data_async(remote_device, 'DATA_REQ')


    """
    Executes on receipt of messages to the coordinator.
    """
    def data_receive_callback(self, xbee_message):
        self.log.debug('BEGIN')
        address = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data.decode('utf8')
        self.log.debug(f'Pushing to the MQTT: Address: {address}, data: {data}, topic {self.config.publish_topic}')
        # Push this to the MQTT broker.
        self.publisher.publish(self.config.publish_topic, xbee_message.data.decode("utf8"))
        
        self.log.debug('END')


    """
    Registers the data handling callback
    """
    def register_listeners(self, data_recevie_callback):
        self.coordinating_device.add_data_received_callback(data_recevie_callback)
        return "OK"

    def _listener(self):
        self.log.debug('Setting the job to running')
        self._running = True
        sleep_time = int(self.config.config_data["sleep-time"])
        while self.is_running():
            self.log.debug('Requesting data')
            self._request_data()

            self.log.debug('Checking for new instructions...')
            status = check_for_instructions(self)
            if "INSTR" == status:
                send_instructions(self)
            elif "OK" != status:
                record_error(self)

            self.log.debug(f'sleeping for {sleep_time}...')
            time.sleep(sleep_time)

        self.log.debug(f'Requested to shut down: is_running={self.is_running()}... ')

    def open(self):
        if( self.coordinating_device is not None and self.coordinating_device.is_open() == False):
            self.coordinating_device.open()

    """
    Closes the connection to the coordinator.
    """
    def close(self):
        if( self.coordinating_device is not None and self.coordinating_device.is_open()):
            self.coordinating_device.close()



"""
The XBee module/classes provides an API wrapper around the XBee Python module
"""
class Sensor(AbstractSensor):

    def __init__(self, config):
        super(Sensor, self).__init__(config, "XBee_Sensor")
        self._sensing_device = None
        self._running = False
        self.log.debug('XBee_Sensor: __init__')
        self._listener_thread = None



    @property
    def sensing_device(self):
        if ( self._sensing_device == None):
            com = self.config.config_data['serial-port']
            baud = int(self.config.config_data['serial-baud'])
            self.log.info(f'Creating a sensor with a connection to {com} at {baud}')
            self._sensing_device = devices.XBeeDevice(com, baud)
            sync_timeout = self._sensing_device.get_sync_ops_timeout()
            self.log.info(f'Synchronous timeout: {sync_timeout}')
            self._sensing_device.set_sync_ops_timeout(10)
        return self._sensing_device

    @sensing_device.setter
    def sensing_device(self, device):
            self._sensing_device = device
            self.log.debug(f"Created Sensing device {self._sensing_device}")


    def _send_data(self, address, payload):
        self.open()
        self.log.info(f'Creating the remote device at {address}')
        remote_device = devices.RemoteXBeeDevice(self.sensing_device, devices.XBee64BitAddress.from_hex_string(address))
        self.log.info(f'Sending from {self.sensing_device.get_64bit_addr()} to {address}')
        self.sensing_device.send_data(remote_device, payload)

    def open(self):
        if( self.sensing_device is not None and self.sensing_device.is_open() == False):
            self.sensing_device.open()

    """
    Closes the connection to the coordinator.
    """
    def close(self):
        if( self.sensing_device is not None and self.sensing_device.is_open()):
            self.sensing_device.close()

