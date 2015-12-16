#!/usr/bin/env python
'''
device_crud.py [-options]
Options:
-h, --help
-c, --create
-r, --read=deviceid
-u, --update=deviceid
-d, --delete=deviceid
'''

import opengate_config as conf
import requests
import uuid
import json
import sys
import getopt

ogapi_devices_uri = '{0}/provision/organizations/{1}/entities/devices'.format(conf.OGAPI_BASE_URI, conf.ORGANIZATION)
headers = {
    'X-ApiKey': conf.API_KEY,
    'Content-Type': 'application/json'
}


def get_device(id, serial=None):
    device = {
        'device': {
            'id': id,
            'provision': {
                'customId': [id],
                'template': 'default',
                'type': 'gateway',
                'specificType': [
                    'CONCENTRATOR'
                ],
                'admin': {
                    'organization': conf.ORGANIZATION,
                    'channel': conf.CHANNEL,
                    'administrativeState': 'ACTIVE',
                    'serviceGroup': 'emptyServiceGroup'
                }
            }
        }
    }

    if serial is not None:
        serials = [serial]
        device['device']['provision']['serialNumber'] = serials

    return device


def create():
    device_id = str(uuid.uuid4())
    device_as_json = json.dumps(get_device(device_id))
    print 'Creating device {0}'.format(device_id)
    print device_as_json
    r = requests.post(ogapi_devices_uri, data=device_as_json, headers=headers)
    print 'Status code received {}'.format(r.status_code)
    print r.text


def read(id):
    print 'Reading device {0}'.format(id)
    uri = '{0}/{1}'.format(ogapi_devices_uri, id)
    r = requests.get(uri, headers=headers)
    print 'Status code received {}'.format(r.status_code)
    print r.text


def update(id, serial):
    print 'Updating device {0}'.format(id)
    device_as_json = json.dumps(get_device(id, serial))
    uri = '{0}/{1}'.format(ogapi_devices_uri, id)
    r = requests.put(uri, data=device_as_json, headers=headers)
    print 'Status code received {}'.format(r.status_code)
    print r.text


def delete(id):
    print 'Deleting device {0}'.format(id)
    uri = '{0}/{1}'.format(ogapi_devices_uri, id)
    r = requests.delete(uri, headers=headers)
    print 'Status code received {}'.format(r.status_code)
    print r.text


def main():
    try:  # parse command line options
        opts, args = getopt.getopt(sys.argv[1:], 'hcr:u:d:', ['help', 'create', 'read=', 'update=', 'delete='])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    if len(opts) is 0:
        print __doc__
        sys.exit(0)

    for o, a in opts:  # process options
        if o in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif o in ('-c', '--create'):
            create()
        elif o in ('-r', '--read'):
            read(a)
        elif o in ('-u', '--update'):
            splited_args = a.split(':')
            update(splited_args[0], splited_args[1])
        elif o in ('-d', '--delete'):
            delete(a)
        else:
            print __doc__
            sys.exit(0)


if __name__ == '__main__':
    main()
