#!/usr/bin/env python

import json
import opengate_config as conf
import requests

from flask import Flask
from flask import request
from device_emulator_common import reboot, update, operation_step_response

app = Flask(__name__)


def publish_operation_step_response(content, device_id, name, result, close_operation):
    ogapi_operation_response_uri = '{0}/devices/{1}/operation/response'.format(
        conf.OG_SOUTH_API_BASE_URI,
        device_id)

    step_response = operation_step_response(content, name, result, close_operation)

    step_response_as_json = json.dumps(step_response, indent=2)

    print 'Publishing {0} step status {1} to {2}...'.format(name, result, ogapi_operation_response_uri)
    print step_response_as_json
    r = requests.post(ogapi_operation_response_uri, data=step_response_as_json, headers=conf.HEADERS, stream=True)
    print '...done'


@app.route('/v70/devices/<device_id>/operation/requests', methods=['POST'])
def opengate_operations_handler(device_id):
    content = request.get_json(force=True)
    print '===================================='
    print 'Request received with for device {0} with the following content'.format(device_id)
    print json.dumps(content, indent=2)
    operation_name = content['operation']['request']['name']
    print 'Operation name got: {0}'.format(operation_name)

    print 'Response:'
    response_as_json = ''
    response_status = 201
    if operation_name == 'REBOOT_EQUIPMENT':
        response_as_json = json.dumps(reboot(content), indent=2)
    elif operation_name == 'UPDATE':
        response_as_json = json.dumps(update(content, device_id, publish_operation_step_response), indent=2)
    else:
        response_status = 400

    print response_as_json
    return response_as_json, response_status


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1123, debug=True)
