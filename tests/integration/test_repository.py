
from leawood.domain.hardware import Sensor
import uuid
import pytest
import logging

class TestRepository:

    logger = logging.getLogger('__name__')
    test_addr = uuid.uuid1().hex[:16]

    def get_addr(self):
        return self.test_addr.upper()

    @pytest.mark.order1
    def test_repository_add_node(self, repository):
        random_addr = self.get_addr()
        node = Sensor()
        node.addr64bit = random_addr
        node.domain = 'POWER'
        node.node_class = 'SENSOR'
        node.serial_id = random_addr
        node.name = f'TEST GENERATED DEVICE {random_addr}'
        node.description = 'A device generated via integration tests'
        node = repository.add_node(node)

        node2 = repository.get_node(random_addr)

        assert node2 != None
        assert node2.serial_id == random_addr.upper()
        assert node2.description == 'A device generated via integration tests'

    @pytest.mark.order2
    def test_repository_get_node(self, repository):
        random_addr = self.get_addr()
        node = repository.get_node(random_addr)
        assert node != None
        assert node.serial_id == random_addr
        assert node.description == 'A device generated via integration tests'


   