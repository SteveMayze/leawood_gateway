
from leawood.config import Config
import pytest
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
def config(pytestconfig):
    return create_config(pytestconfig, 'config.json', 'xbeeport')

