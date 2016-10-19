#!/usr/bin/env python

import paho.mqtt.client as mqtt
import json
import opengate_config as conf
from device_emulator_common import reboot, update, operation_step_response

ODM_SUBSCRIBE_TOPIC = 'odm/request/{0}'
ODM_PUBLISH_RESPONSE_TOPIC = 'odm/response/{0}'
ODM_PUBLISH_DMM_TOPIC = 'odm/dmm/{0}'
ODM_PUBLISH_IOT_TOPIC = 'odm/iot/{0}'


def on_connect(client, userdata, flags, rc):
    print('OpenGate MQTT client Connected with result code '+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(ODM_SUBSCRIBE_TOPIC.format(device_id), qos=1)


def on_message(client, userdata, message):
    print(message.topic+' '+str(message.payload))

    def publish_operation_step_response(content, device_id, name, result, close_operation):
        step_response = operation_step_response(content, name, result, close_operation)
        step_response_as_json = json.dumps(step_response, indent=2)
        print 'Publishing {0} step status {1}...'.format(name, result)
        print step_response_as_json
        client.publish(ODM_PUBLISH_RESPONSE_TOPIC.format(device_id), step_response_as_json, qos=1)
        print '...done'

    content = json.loads(message.payload)
    print '===================================='
    print 'Request received with for device {0} with the following content'.format(device_id)
    print json.dumps(content, indent=2)
    operation_name = content['operation']['request']['name']
    print 'Operation name got: {0}'.format(operation_name)

    print 'Response:'
    response_as_json = ''
    if operation_name == 'REBOOT_EQUIPMENT':
        response_as_json = json.dumps(reboot(content), indent=2)
    elif operation_name == 'UPDATE':
        response_as_json = json.dumps(update(content, device_id, publish_operation_step_response), indent=2)

    print response_as_json
    # Message reception ACK
    client.publish(ODM_PUBLISH_RESPONSE_TOPIC.format(device_id), response_as_json, qos=1)

if __name__ == '__main__':
    print 'OpenGate MQTT client test'

    device_id = None
    if conf.DEFAULT_DEVICE_ID is not None:
        device_id = conf.DEFAULT_DEVICE_ID
    else:
        try:
            device_id_file = open('.device_id', 'r')
            device_id = device_id_file.read().strip()
        except IOError:
            print 'Can\'t read device_id file'

    print 'Device IO got {0}'.format(device_id)

    client = mqtt.Client(client_id=device_id)
    client.username_pw_set(device_id, conf.API_KEY)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(conf.OPENGATE_HOST, conf.SOUTH_MQTT_PORT, 60)
    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a manual interface.
    client.loop_forever()

