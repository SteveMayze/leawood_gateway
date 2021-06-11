from digi.xbee import devices
from leawood.config import Config


class AbstractSensor:

    def __init__(self, config, name):
        self._config = config
        self._log = config.getLogger(name)
        self.log.debug('AbstractSensor: __init__')

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, log):
        self._log = log

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config


"""
The XBee module/classes provides an API wrapper around the XBee Python module
"""
class XBeeSensor(AbstractSensor):

    def __init__(self, config: Config):
        super(AbstractSensor, self).__init__(config, __name__)
        self._sensing_device = None
        self._running = False
        self.log.debug('XBeeSensor: __init__')
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

