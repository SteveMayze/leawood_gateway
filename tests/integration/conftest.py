
from leawood.config import Config
from leawood.domain.hardware import Sensor
from leawood.services import messagebus
from leawood.services.messagebus import LocalMessageBus
from leawood.adapters.xbee import XBeeModem

import pytest
import os


def create_config(pytestconfig, configname):
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, configname)
    cert_path = os.path.join(script_dir, '.ssh')
    args = ['--config', config_path, 
        '--certpath', cert_path]
    return Config(args)

@pytest.fixture
def config(pytestconfig):
    return create_config(pytestconfig, 'config.json')

@pytest.fixture
def sensor(pytestconfig):
    sensor_config = create_config(pytestconfig, 'config-test-sensor.json')
    message_bus = LocalMessageBus()
    modem = XBeeModem(sensor_config)
    sensor = Sensor(message_bus, modem)
    return sensor