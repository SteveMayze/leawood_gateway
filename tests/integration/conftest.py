
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
    cert_path = os.path.join(script_dir, '.ssh')
    args = ['--config', config_path, 
        '--certpath', cert_path]
    return Config(args)

@pytest.fixture
def config():
    return create_config('config.json')

@pytest.fixture
def sensor():
    sensor_config = create_config('config-test-sensor.json')
    message_bus = LocalMessageBus()
    modem = XBeeModem(sensor_config)
    sensor = Sensor(message_bus, modem)
    return sensor

@pytest.fixture
def repository(config)    :
    repository = Rest(config)
    return repository

@pytest.fixture
def gateway(config, repository):
    logger.info(f'Creating a gateway with {config}')
    modem = XBeeModem(config)
    message_bus = LocalMessageBus()
    gateway = Gateway(message_bus, repository, modem)
    messagebus.activate(message_bus)
    wait_for_runnning_state(message_bus, True)
    yield gateway
    messagebus.shutdown(message_bus)
    wait_for_runnning_state(message_bus, False)
    gateway.close()
