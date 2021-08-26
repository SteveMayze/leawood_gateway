
from leawood.config import Config
from leawood.domain.hardware import Sensor, Gateway
from leawood.services import messagebus
from leawood.services.messagebus import LocalMessageBus
from leawood.adapters.xbee import XBeeModem
from leawood.adapters.rest import Rest
import time
import pytest
import os
import logging


logger = logging.getLogger(__name__)

MAX_WAIT = 2

RED = '0013A20041AE49D4'
GREEN = '0013A200415D58CB'
WHITE = '0013A200415C0F82'

def wait_for_runnning_state(worker, state):
    start_time = time.time()
    while True:
        try:
            assert worker.is_running() == state
            return
        except (AssertionError) as error:
            if time.time() - start_time > MAX_WAIT: 
                raise error 
            time.sleep( 0.5)    


def create_config(configname):
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, configname)
    args = ['--config', config_path, 'start']
    return Config(args)

@pytest.fixture
def config():
    return create_config('config.ini')

@pytest.fixture
def sensor():
    sensor_config = create_config('config-test-sensor.ini')
    message_bus = LocalMessageBus()
    modem = XBeeModem(sensor_config)
    sensor = Sensor(message_bus, modem)
    return sensor

@pytest.fixture
def repository(config):
    repository = Rest(config)
    return repository


@pytest.fixture
def is_staged():
    staged = os.environ.get('STAGED')
    if staged == 'True':
        logger.info('Staged')
        return True
    return False

@pytest.fixture
def staging_address():
    staging = os.environ.get('STAGING_GATEWAY')
    return staging

@pytest.fixture
def gateway(config, repository, is_staged):
    gateway = None
    message_bus = None
    if not is_staged:
        logger.info(f'Creating a test gateway with {config}')
        modem = XBeeModem(config)
        message_bus = LocalMessageBus()
        gateway = Gateway(message_bus, repository, modem)
        messagebus.activate(message_bus)
        wait_for_runnning_state(message_bus, True)
    else:
        logger.info(f'Creating dummy gateway')
        gateway = Gateway(None, None, None)
    yield gateway
    if message_bus:
        messagebus.shutdown(message_bus)
        wait_for_runnning_state(message_bus, False)
    gateway.close()
