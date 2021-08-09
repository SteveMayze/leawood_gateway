
from leawood.domain.hardware import Sensor
import uuid

class TestRepository:

    def test_repository_get_node(self, repository):
        node = repository.get_node('0013A200415D58CB')
        assert node != None
        assert node.serial_id == '0013A200415D58CB'
        assert node.description == 'The power monitor  on the mobile chicken coop'


    def test_repository_add_node(self, repository):
        random_addr = uuid.uuid1().hex[:16]
        node = Sensor()
        node.addr64bit = random_addr
        node.domain = 'POWER'
        node.node_class = 'SENSOR'
        node.serial_id = random_addr
        node.name = f'TEST GENERATED DEVICE {random_addr}'
        node.description = 'A device generated via integration tests'
        node = repository.add_node(node)
        assert node != None
        assert node.serial_id == random_addr.upper()
        assert node.description == 'A device generated via integration tests'

