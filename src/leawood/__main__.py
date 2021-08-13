
import logging
import sys
from leawood.config import Config

from leawood.domain.hardware import Gateway
from leawood.services import messagebus
from leawood.services.messagebus import LocalMessageBus
from leawood.adapters.xbee import XBeeModem
from leawood.adapters.rest import Rest
import time


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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(config: Config):
    logger.debug('start begin')
    logger.info(f'Creating a gateway with {config}')
    repository = Rest(config)
    modem = XBeeModem(config)
    message_bus = LocalMessageBus()
    gateway = Gateway(message_bus, repository, modem)
    messagebus.activate(message_bus)
    wait_for_runnning_state(message_bus, True)
    try:
        while True:
            message_bus.listener_thread.join(10)
            logger.info('heartbeat')
    except KeyboardInterrupt:
        logger.info('key board interrupt. Closing down')
        pass
    messagebus.shutdown(message_bus)
    wait_for_runnning_state(message_bus, False)
    gateway.close()
    logger.debug('end')

def stop(config: Config):
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
    cmd(config)
    logger.debug(f'end')