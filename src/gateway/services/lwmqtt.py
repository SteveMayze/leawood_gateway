import paho.mqtt.client as mqtt
from leawood.config import Config
from leawood.lwrest import Rest
import json
import os
import logging
import ssl

from json import JSONEncoder


def start_message_handler(message_handler):
    message_handler.set_on_connect_callback(message_handler.on_connect)
    message_handler.set_on_subscribe_callback(message_handler.on_subscribe)
    message_handler.set_on_message_callback(message_handler.on_message)
    message_handler.start()
    return "OK"

##
## Subscriber
class Subscriber:
    def __init__(self, config):
        self.config = config
        self.log = config.getLogger('lwmqtt.Subscriber')
        self.log.info(f'Initialising the Subscriber')
        self._client = None

    @property
    def client(self):
        if self._client == None:
            self._client = mqtt.Client(protocol=mqtt.MQTTv311, userdata=self)
            cacert = os.path.join(self.config.config_data['certpath'], self.config.config_data['cacert'])
            clientcert = os.path.join(self.config.config_data['certpath'], self.config.config_data['clientcrt'])
            clientkey = os.path.join(self.config.config_data['certpath'], self.config.config_data['clientkey'])
            self.log.info('Setting up the certificates')
            self.log.info(f"CA certificate: {cacert}")
            self.log.info(f"Client certificate: {clientcert}")
            self.log.info(f"Client key: {clientkey}")
            self._client.tls_set(
                ca_certs = cacert, 
                certfile = clientcert, 
                keyfile  = clientkey,
                tls_version = ssl.PROTOCOL_TLSv1_1
                )
            self._client.tls_insecure_set(True)
        return self._client


    @client.setter
    def client(self, value):
        self._client = value

    def __enter__(self): 
        config = self.config
        self.log.info("Connecting")
        self.client.connect( host=config.config_data['mqttserver'], port=int(config.config_data['mqttport']), keepalive = 60)
        return self.client
  
    def __exit__(self, exc_type, exc_value, traceback):
        # self.log.info(f'exec_type: {exec_type}, exec_value: {exec_value}, traceback: {traceback}') 
        self.log.info("Disconnecting")
        self.client.disconnect

    def on_connect(self, client, userdata, flags, rc):
        userdata.log.info(f'Result from connect: {mqtt.connack_string(rc)}')
        # Subscribe to the power/sensor/+/data
        client.subscribe(userdata.config.subscribe_topic, qos=2)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        userdata.log.info(f'I have subscribed with QoS {granted_qos[0]}')

    def on_message(self, client, userdata, msg):
        userdata.log.info(f'Message received. Topic: {msg.topic}, payload {str(msg.payload)}')
        qData = json.loads(msg.payload)
        rest = Rest(userdata.config)
        response = rest.post("data_points", JSONEncoder().encode(qData).encode("utf-8"))
        userdata.log.info(f'Response: {response.status_code}')
        if response.status_code != 200:
            userdata.log.error(f' ERROR {response.text}')
            raise()

    def set_on_connect_callback(self, on_connect):
        self.client.on_connect = on_connect

    def set_on_subscribe_callback(self, on_subscribe):
        self.client.on_subscribe =  on_subscribe
    
    def set_on_message_callback(self, on_message):
        self.client.on_message =  on_message

    def start(self):
        config = self.config
        self.log.info("Starting the subscriber")
        self.log.info(f"Connecting host={config.config_data['mqttserver']}, port={int(config.config_data['mqttport'])}")
        self.client.connect( host=config.config_data['mqttserver'], port=int(config.config_data['mqttport']), keepalive = 60)
        self.client.loop_start()


    def close(self):
        self.log.info("Stopping the subscriber")
        self.client.loop_stop()



##
## Publisher
class Publisher:
    def __init__(self, config):
        self.config = config
        self.log = config.getLogger("lwmqtt.Publisher")
        self.log.info(f'Initialising the Publisher')
        self._client = None


    @property
    def client(self):
        if self._client == None:
            # self.client = mqtt.Client(protocol=mqtt.MQTTv311, userdata=self)
            self._client = mqtt.Client(protocol=mqtt.MQTTv311, userdata=self)
            cacert = os.path.join(self.config.config_data['certpath'], self.config.config_data['cacert'])
            clientcert = os.path.join(self.config.config_data['certpath'], self.config.config_data['clientcrt'])
            clientkey = os.path.join(self.config.config_data['certpath'], self.config.config_data['clientkey'])
            self.log.info('Setting up the certificates')
            self.log.info(f"CA certificate: {cacert}")
            self.log.info(f"Client certificate: {clientcert}")
            self.log.info(f"Client key: {clientkey}")
            self._client.tls_set(
                ca_certs = cacert, 
                certfile = clientcert, 
                keyfile  = clientkey,
                tls_version = ssl.PROTOCOL_TLSv1_1
                )
            self._client.tls_insecure_set(True)
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def __enter__(self): 
        config = self.config
        #  "C:\Program Files\mosquitto\mosquitto_sub" -h 192.168.178.45 -V mqttv311 -p 8883 
        # --cafile ca.crt --cert hub001.crt --key hub001.key -t "power/sensor/0013A20041629BFB/data"

        self.log.info(f"Connecting host={config.config_data['mqttserver']}, port={int(config.config_data['mqttport'])}")
        self.client.connect( host=config.config_data['mqttserver'], port=int(config.config_data['mqttport']), keepalive = 60)
        return self.client
  
    def __exit__(self, exc_type, exc_value, traceback):
        # self.log.info(f'exec_type: {exec_type}, exec_value: {exec_value}, traceback: {traceback}') 
        self.log.info("Disconnecting")
        self.client.disconnect

 

    def publish(self, topic, payload):
        config = self.config
        self.log.info(f"Connecting host={config.config_data['mqttserver']}, port={int(config.config_data['mqttport'])}")
        self.client.connect( host=config.config_data['mqttserver'], port=int(config.config_data['mqttport']), keepalive = 60)
        self.log.info(f"Publishing {payload}")
        self.client.publish(
            topic = topic,
            payload = payload
        )
        # self.client.disconnect

