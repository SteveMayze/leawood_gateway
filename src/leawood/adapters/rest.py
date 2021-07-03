
import requests
from requests.auth import HTTPBasicAuth

import logging
from leawood.domain.hardware import Sensor

from leawood.services.repository import Repository
from leawood.domain.model import Node
from leawood.domain.messages import Message

logger = logging.getLogger(__name__)


class Rest(Repository):

    def __init__(self, config):
        self.config = config

    def get(self, resource, query = None):
        ## Get the device details
        log = logger
        config = self.config
        payload={}
        base_url = config.config_data['rest']
        headers = { f'Authorization': 'Basic {url_auth}'}
        if not query:
            url = f'{base_url}/{resource}'
        else:
            url = f'{base_url}/{resource}?q={query}'
        log.info (f'GET {url}\n  query: {query}')
        response =  requests.request("GET", url, headers=headers, data=payload, timeout=30, auth=HTTPBasicAuth(config.config_data['username'], config.config_data['password']))
        log.info(f"response: {response.json()['items'][0]}")
        return response.json()['items'][0]

    def post(self, resource, payload):
        ## Get the device details
        log = self.log
        config = self.config
        base_url = config.config_data['rest']
        headers = {
            'Content-Type': 'application/json',
        ## f'Authorization': 'Basic {url_auth}'
        }
        url = f'{base_url}/{resource}'
        log.info (f'POST {url}\n   payload: {payload}\n user {config.config_data["username"]}, pwd: {config.config_data["password"]}')
        return requests.request(
            "POST", url, headers=headers, data=payload, timeout=30, 
            auth=HTTPBasicAuth(config.config_data['username'], config.config_data['password'])
        )


    

    def _get_node(self, addr64bit: str) -> Node:
        
        resource = f'devices?q={{"address":{{"$eq":"{addr64bit}"}}}}'
        item = self.get(resource)

        node = Sensor()
        node.addr64bit = addr64bit
        node.device_id = item['device_id']
        node.node_class = item['class']
        node.name = item['name']
        node.serial_id = item['serial_id']
        node.description = item['description']
        node.location = item['location']
        node.domain = item['domain']
        return node

    def _add_node(self, sensor: Node):
        pass

    def _post_sensor_data(self, messasge: Message):
        pass
