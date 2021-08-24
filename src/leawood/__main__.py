
import logging
import sys
from leawood.config import Config

from leawood.domain.hardware import Gateway
from leawood.services import messagebus
from leawood.services.messagebus import LocalMessageBus
from leawood.adapters.xbee import XBeeModem
from leawood.adapters.rest import Rest
import time
import uuid
from pathlib import Path

MAX_WAIT = 2

pid = Path('~/.leawood/pid')
pid = pid.expanduser()

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

logging.basicConfig(filename='leawood_gateway.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(config: Config):
    logger.debug('start begin')
    logger.info('Checkig PID')
    # On the Pi, the /dev/urandom is not available on startup. It is not known
    # when or how this is avaialble as using uuid.uuid4() worked up until a 
    # cold restart.
    uid = str(uuid.uuid1())
    if not pid.parent.exists():
        logger.info(f'Creating {pid.parent}')
        pid.parent.mkdir()

    if pid.exists():
        logger.debug(f'The PID {pid} already exists ... overwriting')
        pid.unlink()

    logger.debug(f'Creating PID {pid} with {uid}')
    pid.write_text(f'{uid}')

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
            logger.debug('heartbeat')
            if pid.exists():
                check = pid.read_text()
                if not check == uid:
                    logger.info('The PID has changed. Shutting this thread down.')
                    break
            else:
                logger.info('The PID has been removed. Shutting this thread down.')
                break

    except KeyboardInterrupt:
        logger.info('key board interrupt. Closing down')
        pass
    messagebus.shutdown(message_bus)
    wait_for_runnning_state(message_bus, False)
    gateway.close()
    logger.debug('end')

def stop(config: Config):
    logger.debug('stop begin')
    if pid.exists():
        pid.unlink()
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