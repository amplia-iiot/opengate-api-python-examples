#!/usr/bin/env python

import json
import websocket
import opengate_config as conf
from device_emulator_common import reboot, update, field_diagnostic, configreport, operation_step_response


def on_message(ws, message):

    def publish_operation_step_response(content, device_id, name, result, close_operation):
        step_response = operation_step_response(content, name, result, close_operation)
        step_response_as_json = json.dumps(step_response, indent=2)
        print('Publishing {0} step status {1}...'.format(name, result))
        print(step_response_as_json)
        ws.send(step_response_as_json)
        print('...done')

    content = json.loads(message)
    print('====================================')
    print('Request received with for device {0} with the following content'.format(device_id))
    print(json.dumps(content, indent=2))
    operation_name = content['operation']['request']['name']
    print('Operation name got: {0}'.format(operation_name))

    print('Response:')
    response_as_json = ''
    if operation_name == 'REBOOT_EQUIPMENT':
        response_as_json = json.dumps(reboot(content), indent=2)
    elif operation_name == 'UPDATE':
        response_as_json = json.dumps(update(content, device_id, publish_operation_step_response), indent=2)
    elif operation_name == 'FIELD_DIAGNOSTIC':
        response_as_json = json.dumps(field_diagnostic(content), indent=2)
    elif operation_name == 'CONFIGREPORT':
        response_as_json = json.dumps(configreport(content), indent=2)

    print(response_as_json)
    # Message reception ACK
    ws.send(response_as_json)


def on_error(ws, error):
    print('WebSocket error')
    print(error)


def on_close(ws):
    print('WebSocket closed')


def on_open(ws):
    print('WebSocket opened')


if __name__ == "__main__":
    print('OpenGate WebSocket Client')

    device_id = None
    if conf.DEFAULT_DEVICE_ID is not None:
        device_id = conf.DEFAULT_DEVICE_ID
    else:
        try:
            device_id_file = open('.device_id', 'r')
            device_id = device_id_file.read().strip()
        except IOError:
            print('Can\'t read device_id file')

    if device_id is None:
        print('No device id available')
        sys.exit(2)

    websocket.enableTrace(True)
    opengate_websocket_uri = '{0}/{1}?X-ApiKey={2}'.format(conf.OG_SOUTH_WEBSOCKET_BASE_URI, device_id, conf.API_KEY)
    print('Opening websocket on {0}'.format(opengate_websocket_uri))
    ws = websocket.WebSocketApp(opengate_websocket_uri, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open

    ws.run_forever()
