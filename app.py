#!/usr/bin/env python

import json
from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/v70/devices/<device_id>/operation/requests', methods=['POST'])
def opengate_operations_handler(device_id):
    content = request.get_json(force=True)
    print '===================================='
    print 'Request received with for device {0} with the following content'.format(device_id)
    print content
    print json.dumps(content, indent=2)
    operation_name = content['operation']['request']['name']
    print 'Extracted operation name {0}'.format(operation_name)

    if operation_name is 'REBOOT_EQUIPMENT':
        print 'Performing the reboot of the equipment'

    response = {
        "version": "7.0",
        "operation": {
            "response": {
                "timestamp": 1432454278000,
                "name": operation_name,
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

    return json.dumps(response), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1123, debug=True)
