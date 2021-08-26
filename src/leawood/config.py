
import argparse
import logging
import configparser

logger = logging.getLogger(__name__)

class Config:

    def __init__(self, args):
        self._config_data = self.handle_config(self.parse_args(args=args) )
        self._debug = self.config_data["debug"]

    @property
    def config_data(self):
        return self._config_data

    @property
    def debug(self):
        return self._debug


    @property
    def subscribe_topic(self):
        return self._subscribe_topic

    @subscribe_topic.setter
    def subscribe_topic(self, value):
        self._subscribe_topic = value
        
    @property
    def publish_topic(self):
        return self._publish_topic

    @publish_topic.setter
    def publish_topic(self, value):
        self._publish_topic = value


    def parse_args(self, args):
        parser = argparse.ArgumentParser(description="Start and stop the gateway")
        parser.add_argument('-c', '--config', metavar='config_file', required=False, dest='config', action='store', help='The configuration file containing the common arguments')
        parser.add_argument('-v', '--verbose', required=False, dest='debug', action='store_true', help='Enable debug mode')
        parser.add_argument('-u', '--username', metavar='user_name', required=False, dest='username', action='store', help='The username for the REST service')
        parser.add_argument('-w', '--password', metavar='password', required=False, dest='password', action='store', help='The password for the REST service')
        parser.add_argument('-l', '--logfile', metavar='logfile', required=False, dest='logfile', action='store', help='The name of the log file')
        parser.add_argument('-r', '--rest', metavar='rest', required=False, dest='rest', action='store', help='The base ReST endpoint')
        parser.add_argument('-s', '--serial-port', metavar='serial-port', required=False, dest='serialport', action='store', help='The serial port for the XBee module')
        parser.add_argument('-b', '--baud', metavar='baud', required=False, dest='baud', action='store', help='The baud rate for the XBee module')
        parser.add_argument('-S', '--sleeptime', metavar='sleeptime', required=False, dest='sleeptime', action='store', help='The sleep time when waiting to request new information')
        ### parser.add_argument('command', choices=['start', 'stop'], help='Start the gateway process' )
        subparsers = parser.add_subparsers(dest='command')
        start_parser = subparsers.add_parser('start')
        start_parser = subparsers.add_parser('stop')
        parsed_args = parser.parse_args(args)
        return parsed_args


    def handle_config(self, args):
        debug = args.debug
        configFile = args.config
        config = configparser.ConfigParser()

        if ( debug ):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        config_data = {}
        logger.debug(f"Command line args: {args}")

        if configFile != None:
            logger.debug(f'The config file is set to {configFile}' )
            config.read(configFile)
            config_data = config._sections['general']
            config_data.update(config._sections['rest'])
            config_data.update(config._sections['modem'])
            logger.debug(f'handle_config: initial config_data={config}')

        if args.debug != None:
            if 'debug' in config_data:
                config_data.pop('debug')
            config_data['debug'] = debug
        else:
            logger.debug( 'debug is not set on the command line')
            if 'debug' in config_data:
                config_data.pop('debug')
            config_data['debug'] = 'False'

        if args.username != None:
            config_data['username'] = args.username

        if args.password != None:
            config_data['password'] = args.password

        if args.rest != None:
            logger.debug( f'REST Set. Setting the base REST URL {args.rest}')
            config_data['rest'] = args.rest

        if args.logfile != None:
            config_data['logfile'] = args.logfile

        if args.serialport != None:
            logger.debug( f'Serial Port: {args.serialport}')
            config_data['serial-port'] = args.serialport

        if args.baud != None:
            logger.debug( f'Baud Rate: {args.baud}')
            if 'serial-baud' in config_data:
                config_data.pop('serial-baud')
            config_data['serial-baud'] = args.baud

        if args.sleeptime != None:
            if 'sleep-time' in config_data:
                config_data.pop('sleep-time')
            logger.debug( f'Sleep time: {args.sleeptime}')
            config_data['sleep-time'] = args.sleeptime

        if args.command != None:
            logger.debug( f'Command: {args.command}')
            config_data['command'] = args.command

        logger.debug(f'config_data: {config_data}')
        return config_data

