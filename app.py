#!/usr/bin/env python

import opengate_config as conf
import json
from flask import Flask
from flask import request
import requests

app = Flask(__name__)

headers = {
    'X-ApiKey': conf.API_KEY,
    'Content-Type': 'application/json'
}


def reboot():
    print 'Simulating the reboot of the equipment'
    response = {
        "version": "7.0",
        "operation": {
            "response": {
                "timestamp": 1432454278000,
                "name": 'REBOOT_EQUIPMENT',
                "id": "12345667890",
                "resultCode": "SUCCESSFUL",
                "resultDescription": "No Error.",
                "variableList": [],
                "steps": [
                    {
                        "name": "REBOOT_EQUIPMENT",
                        "timestamp": 1432454278000,
                        "result": "SUCCESSFUL",
                        "description": "Hardware reboot Ok"
                    }
                ]
            }
        }
    }
    return response


def update(content):
    parameters = content['operation']['request']['parameters']
    for parameter in parameters:
        if parameter['name'] == 'deploymentElements':
            deployment_elements = parameter['value']['array']
            for deployment_element in deployment_elements:
                download_url = deployment_element['downloadUrl']
                file_path = deployment_element['path']
                print 'Downloading {0}...'.format(download_url)
                r = requests.get(download_url, headers=headers, stream=True)
                print 'Status code received {}'.format(r.status_code)
                if r.status_code == 200:
                    print 'Writting file to disk...'
                    with open(file_path, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                    print '...done'
                else:
                    print 'Something went wrog'

    response = {
        "version": "7.0",
        "operation": {
            "response": {
                "timestamp": 1432454278000,
                "name": 'UPDATE',
                "id": "12345667890",
                "resultCode": "SUCCESSFUL",
                "resultDescription": "No Error.",
                "variableList": [],
                "steps": []
            }
        }
    }
    return response


@app.route('/v70/devices/<device_id>/operation/requests', methods=['POST'])
def opengate_operations_handler(device_id):
    content = request.get_json(force=True)
    print '===================================='
    print 'Request received with for device {0} with the following content'.format(device_id)
    print content
    print json.dumps(content, indent=2)
    operation_name = content['operation']['request']['name']
    print 'Operation name got: {0}'.format(operation_name)

    response = '', 400  # Default response is Bad Request
    if operation_name == 'REBOOT_EQUIPMENT':
        response = json.dumps(reboot()), 201
    elif operation_name == 'UPDATE':
        response = json.dumps(update(content)), 201

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1123, debug=True)
