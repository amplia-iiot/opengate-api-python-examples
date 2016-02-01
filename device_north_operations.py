#!/usr/bin/env python
'''
device_north_operations.py [-options]
Options:
-h, --help
-r, --reboot
'''

import opengate_config as conf
import requests
import json
import sys
import getopt

OPERATION_NAME_REBOOT = 'REBOOT_EQUIPMENT'
OPERATION_NAME_UPDATE = 'UPDATE'

ogapi_jobs_uri = '{0}/operation/jobs'.format(conf.OG_NORTH_API_BASE_URI)

headers = {
    'X-ApiKey': conf.API_KEY,
    'Content-Type': 'application/json'
}


def http_post(entity_id, entity_as_json, entity_uri):
    print 'Sending job to device {0}'.format(entity_id)
    print entity_as_json
    r = requests.post(entity_uri, data=entity_as_json, headers=headers)
    print 'Status code received {}'.format(r.status_code)


def reboot(device_id):
    reboot_job = {
        'job': {
            'request': {
                'name': OPERATION_NAME_REBOOT,
                'parameters': [{'name': 'type', 'type': 'string', 'value': {'string': 'HARDWARE'}}],
                'active': True,
                'notify': False,
                'userNotes': 'Reboot equipment test',
                'schedule': {'stop': {'delayed': '150000'}},
                'operationParameters': {'timeout': 60000},
                'target': {'append': {'entities': [device_id]}}
            }
        }
    }
    job_as_json = json.dumps(reboot_job, indent=2)
    http_post(device_id, job_as_json, ogapi_jobs_uri)


def update(device_id):
    update_job = {
        'job': {
            'request': {
                'name': 'UPDATE',
                'parameters': [
                    {'name': 'bundleName', 'value': {'string': conf.BUNDLE_NAME}},
                    {'name': 'bundleVersion', 'value': {'string': conf.BUNDLE_VERSION}}
                ],
                'active': True,
                'schedule': {'stop': {'delayed': 300000}},
                'operationParameters': {'timeout': 60000},
                'target': {
                    'append': {
                        'entities': [device_id]
                    }
                }
            }
        }
    }
    job_as_json = json.dumps(update_job, indent=2)
    http_post(device_id, job_as_json, ogapi_jobs_uri)


def load_id():
    device_id = None

    if conf.DEFAULT_DEVICE_ID is not None:
        device_id = conf.DEFAULT_DEVICE_ID
    else:
        try:
            device_id_file = open('.device_id', 'r')
            device_id = device_id_file.read().strip()
        except IOError:
            print 'Can\'t read device_id file'

    return device_id


def main():
    try:  # parse command line options
        opts, args = getopt.getopt(sys.argv[1:], 'hru', ['help', 'reboot', 'update'])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    if len(opts) is 0:
        print __doc__
        sys.exit(0)

    device_id = load_id()

    for o, a in opts:  # process options
        if o in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif o in ('-r', '--read'):
            reboot(device_id)
        elif o in ('-u', '--update'):
            update(device_id)
        else:
            print __doc__
            sys.exit(0)


if __name__ == '__main__':
    main()
