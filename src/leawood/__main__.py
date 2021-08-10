
import logging
import sys
from leawood.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start():
    logger.debug('start begin')
    logger.debug('start end')

def stop():
    logger.debug('stop begin')
    logger.debug('stop end')


if __name__ == "__main__":
    config = Config(sys.argv[1:])
    log_level = config.debug

    logger_level = {
        True: logging.DEBUG,
        False: logging.INFO
    }[log_level]

    logger.setLevel(logger_level)

    logger.debug(f'begin')   
    logger.debug(f'command: {config.config_data["command"]}')

    cmd = {
        'start': start,
        'stop': stop,
    }[config.config_data['command']]
    cmd()
    logger.debug(f'end')