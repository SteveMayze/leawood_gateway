
import requests
from requests.auth import HTTPBasicAuth

class Rest:

    def __init__(self, config):
        self.config = config
        self.log = config.getLogger("lwrest.Rest")


    def get(self, resource, query = None):
        ## Get the device details
        log = self.log
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


        

