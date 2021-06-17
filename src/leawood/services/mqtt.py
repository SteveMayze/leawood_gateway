
import logging
import abc
from leawood.domain.model import Message

logger = logging.getLogger(__name__)



class MQTT(abc.ABC):
    @abc.abstractmethod
    def publish(self, message: Message):
        raise NotImplementedError


def shutdown(mqtt: MQTT):
    logger.info(f'Shutting down the mqtt bus')

def activate(mqtt: MQTT):
    logger.info(f'Activating the mqtt bus')

def publish(mqtt: MQTT, message: Message):
    logger.info(f'Publishing a message')
    mqtt.publish(message)
