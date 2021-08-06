
import requests
from requests.auth import HTTPBasicAuth

import logging
from leawood.domain.hardware import Sensor

from leawood.services.repository import Repository
from leawood.domain.model import Node
from leawood.domain.messages import Message
import json

logger = logging.getLogger(__name__)


class Rest(Repository):
    """
    The Rest class is an implmenetation of the Repository abstract class
    to provide a REST implemenation of a persistence layer.
    """
    def __init__(self, config):
        self.config = config

    def _http_get(self, resource, query = None):
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
        if response.status_code != 200:
            raise
        response_doc = response.json()
        if 'items' in response_doc and len(response_doc['items']) > 0:
            log.info(f"response: {response_doc['items'][0]}")
            return response.json()['items'][0]
        else:
            return None

    def _http_post(self, resource, payload):
        ## Get the device details
        log = logger
        config = self.config
        base_url = config.config_data['rest']
        headers = {
            'Content-Type': 'application/json',
        ## f'Authorization': 'Basic {url_auth}'
        }
        url = f'{base_url}/{resource}'
        log.info (f'POST {url}\n   payload: {payload}\n user {config.config_data["username"]}, pwd: {config.config_data["password"]}')
        response =  requests.request(
            "POST", url, headers=headers, data=payload, timeout=30, 
            auth=HTTPBasicAuth(config.config_data['username'], config.config_data['password'])
        )
        if response.status_code != 200:
            raise
        return response.json()['response']


    

    def _get_node(self, serial_id: str) -> Node:
        
        resource = 'devices'
        query = f'{{"serial_id":{{"$eq":"{serial_id}"}}}}'
        item = self._http_get(resource, query)

        if item != None:
            ## TODO - The creation of the Sensor should be based on the domain and class
            ##        of the device to pick up any specific features and properties.
            node = Sensor()
            node.serial_id = serial_id
            node.device_id = item['device_id']
            node.node_class = item['class']
            node.name = item['name']
            node.addr64bit = item['address']
            node.description = item['description']
            node.location = item['location']
            node.domain = item['domain']
            return node
        return None

    def _add_node(self, node: Node) -> Node:
        payload = json.dumps(node.__dict__)
        response = self._http_post('devices', payload)
        return self.get_node(node.serial_id)

    def _post_sensor_data(self, node: Node, message: Message):
        """
        {
            "serial_id": "0013A200415D58CB",
            "data": [{"bus_voltage": 10.56}]
        }
        """
        payload = {}
        payload['serial_id'] = message.serial_id
        data = []
        for name, val in message.payload.items():
            data_element = {}
            data_element[name] = val
            data.append(data_element)
        payload['data'] = data
        payload = json.dumps(payload)
        logger.info(f'Posting {payload}')
        self._http_post('data_points', payload)
        

