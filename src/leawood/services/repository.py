

import abc
from leawood.domain.messages import Message
from leawood.domain.model import Node

class RepositoryError(Exception):
    """
    An exception to indicate an persistence error
    """
    def __init__(self, message: Message, args: object) -> None:
        super().__init__(*args)
        self.message = message

class Repository(abc.ABC):
    """"
    The respository is a abstract class to represent some type of
    persistence layer. This class is agnostic to the actual physical
    storage layer.
    """

    node_cache = {}

    def __init__(self) -> None:
        self.node_cache = {}

    def get_node(self, serial_id: str) -> Node:
        if serial_id in self.node_cache:
            return self.node_cache[serial_id]
        else:
            node = self._get_node(serial_id)
            if node != None:
                self.node_cache[node.serial_id] = node
                return node
        return None
    

    def post_sensor_data(self, message: Message):
        node = self.get_node(message.serial_id)
        if node:
            self._post_sensor_data(node, message)
        else:
            raise RepositoryError(message, 'The message does not correspond to a known node.')

    def add_node(self, node: Node):
        new_node = self._add_node(node)
        self.node_cache[node.serial_id] = new_node
        return new_node

    @abc.abstractmethod
    def _get_node(self, serial_id: str) -> Node:
        raise NotImplementedError

    @abc.abstractmethod
    def _add_node(self, node: Node) -> Node:
        raise NotImplementedError

    @abc.abstractmethod
    def _post_sensor_data(self, node: Node, message: Message):
        raise NotImplementedError
