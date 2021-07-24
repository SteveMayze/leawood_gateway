

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

    def get_node(self, addr64bit: str) -> Node:
        if addr64bit in self.node_cache:
            return self.node_cache[addr64bit]
        else:
            node = self._get_node(addr64bit)
            if node != None:
                self.node_cache[node.addr64bit] = node
                return node
        return None
    

    def post_sensor_data(self, message: Message):
        node = self.get_node(message.addr64bit)
        if node:
            self._post_sensor_data(node, message)
        else:
            raise RepositoryError(message, 'The message does not correspond to a known node.')

    def add_node(self, node: Node):
        new_node = self._add_node(node)
        self.node_cache[node.addr64bit] = new_node
        return new_node

    @abc.abstractmethod
    def _get_node(self, addr64bit: str) -> Node:
        raise NotImplementedError

    @abc.abstractmethod
    def _add_node(self, node: Node) -> Node:
        raise NotImplementedError

    @abc.abstractmethod
    def _post_sensor_data(self, node: Node, message: Message):
        raise NotImplementedError
