from leawood.config import Config

class TestCase:

    def test_basic(self):
        args = ["-f", "one"]
        config = Config(args)
        assert config.config_data['file'] == 'one'

    def test_basic_debug(self):
        args = ["-f", "one", "-v"]
        config = Config(args)
        assert config.config_data['file'] == 'one'
        assert config.debug

    def test_config_file(self):
        args = ["-v", "--config", "tests/sample-config.json"]
        config = Config(args)
        assert config.config_data['username'] == 'REST_USER'
        assert config.config_data['password'] == 'PASSWORD-NOT-SET'

    def test_basic_xbee_config(self):
        args = ["--serial-port", "COM1", "--baud", "9600"]
        config = Config(args)
        assert config.config_data['serial-port'] == 'COM1'
        assert config.config_data['serial-baud'] == '9600'
