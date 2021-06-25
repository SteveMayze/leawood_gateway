

import abc
from leawood.domain.model import Message, Node

class Repository(abc.ABC):

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
    
    @abc.abstractmethod
    def _get_node(self, addr64bit: str) -> Node:
        raise NotImplementedError

    @abc.abstractmethod
    def _add_node(self, sensor: Node):
        raise NotImplementedError

    @abc.abstractmethod
    def _post_sensor_data(self, messasge: Message):
        raise NotImplementedError
