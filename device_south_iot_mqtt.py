#!/usr/bin/env python
'''
This module emulates a device connected to OpenGate
using MQTT protocol.
'''

import functools
import json
import time
import signal
import sys

import paho.mqtt.client as mqtt
import opengate_config as conf
import device_south_iot_common

ODM_SUBSCRIBE_TOPIC = 'odm/request/{0}'
ODM_PUBLISH_RESPONSE_TOPIC = 'odm/response/{0}'
ODM_PUBLISH_DMM_TOPIC = 'odm/dmm/{0}'
ODM_PUBLISH_IOT_TOPIC = 'odm/iot/{0}'

DEVICE_ID = None
REQUEST = 0

print = functools.partial(print, flush=True)

def signal_handler(signal, frame):
    '''Manage Ctrl+C'''
    print('\nBye')
    sys.exit(0)

def send_request(caller_mqtt_client, request):
    payload = json.dumps(device_south_iot_common.get_data_points(DEVICE_ID), indent=2)
    info = caller_mqtt_client.publish(ODM_PUBLISH_IOT_TOPIC.format(DEVICE_ID), payload, qos=1)
    print('Message %d (result code = %s) = %s' % (info.mid, info.rc, payload))

def on_connect(caller_mqtt_client, userdata, flags, result_code):
    '''`on_connect` callback implementation'''
    print('OpenGate MQTT client Connected with result code ' + str(result_code))
    if result_code != 0: sys.exit(1)

    print('Sending IoT data from device {0} to topid {1}'.format(DEVICE_ID, ODM_PUBLISH_IOT_TOPIC))
    send_request(caller_mqtt_client, REQUEST)

def on_publish(caller_mqtt_client, userdata, mid):
    '''`on_publish` callback implementation'''
    global REQUEST
    print('Message %d has been published' % mid)
    REQUEST += 1
    if REQUEST == 5: sys.exit(0)
    time.sleep(5)
    send_request(caller_mqtt_client, REQUEST)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    print('OpenGate MQTT client test')

    if conf.DEFAULT_DEVICE_ID is not None:
        DEVICE_ID = conf.DEFAULT_DEVICE_ID
    else:
        try:
            DEVICE_ID_FILE = open('.device_id', 'r')
            DEVICE_ID = DEVICE_ID_FILE.read().strip()
        except IOError:
            print('Can\'t read device_id file')
    print('Device ID got {0}'.format(DEVICE_ID))

    MQTT_CLIENT = mqtt.Client(client_id=DEVICE_ID)
    MQTT_CLIENT.username_pw_set(DEVICE_ID, conf.API_KEY)
    MQTT_CLIENT.on_connect = on_connect
    MQTT_CLIENT.on_publish = on_publish

    print('Connect to {}:{}'.format(conf.OPENGATE_HOST, conf.SOUTH_MQTT_PORT))
    MQTT_CLIENT.connect(conf.OPENGATE_HOST, conf.SOUTH_MQTT_PORT, 60)
    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a manual interface.
    MQTT_CLIENT.loop_forever()
