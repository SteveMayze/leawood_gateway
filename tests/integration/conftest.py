
from leawood.lwmqtt import Publisher
from leawood.lwmqtt import Subscriber
import pytest
from leawood.config import Config
from leawood.xbee import Coordinator
from leawood.xbee import Sensor
import os

def pytest_addoption(parser):
    parser.addoption("--xbeeport", action='store', help='Set the serial/com port for the coordinator device', default='COM6')
    parser.addoption("--sensorxbeeport", action='store', help='Set the serial/com port for the sensor device', default='COM7')


def create_config(pytestconfig, configname, portname):
    port = pytestconfig.getoption(portname)
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, configname)
    cert_path = os.path.join(script_dir, '.ssh')
    args = ['--serial-port', port, 
        '--config', config_path, 
        '--certpath', cert_path]
    return Config(args)


@pytest.fixture
def coord_config(pytestconfig):
    return create_config(pytestconfig, 'config.json', 'xbeeport')


@pytest.fixture
def sensor_config(pytestconfig):
    return create_config(pytestconfig, 'config-test-sensor.json', 'sensorxbeeport')


@pytest.fixture
def coordinator(coord_config):
    publisher = Publisher(coord_config)
    coordinator = Coordinator(coord_config, publisher)
    yield coordinator
    coordinator.close()



@pytest.fixture
def sensor(sensor_config):
    sensor = Sensor(sensor_config)
    yield sensor
    sensor.close()

@pytest.fixture
def message_handler(coord_config):
    message_handler = Subscriber(coord_config)
    yield message_handler
    message_handler.close()