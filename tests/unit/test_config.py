from leawood.config import Config

class TestCase:

    def test_basic(self):
        args = ['-u', 'one']
        config = Config(args)
        assert config.config_data['username'] == 'one'
        assert 'command' not in config.config_data


    def test_basic_command(self):
        args = ['-u', 'one', 'start']
        config = Config(args)
        assert config.config_data['username'] == 'one'
        assert config.config_data['command'] == 'start'

    def test_basic_debug(self):
        args = ['-u', 'one', '-v']
        config = Config(args)
        assert config.config_data['username'] == 'one'
        assert config.debug

    def test_config_file(self):
        args = ['-v', '--config', 'tests/sample-config.ini']
        config = Config(args)
        assert config.config_data['username'] == 'REST_USER'
        assert config.config_data['password'] == 'PASSWORD-NOT-SET'

    def test_basic_xbee_config(self):
        args = ['--serial-port', 'COM1', '--baud', '9600']
        config = Config(args)
        assert config.config_data['serial-port'] == 'COM1'
        assert config.config_data['serial-baud'] == '9600'
