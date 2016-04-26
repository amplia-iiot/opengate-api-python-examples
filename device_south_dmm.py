#!/usr/bin/env python
'''
device_south_dmm.py [-options]
Options:
-h, --help
-i, --identifier=deviceid
'''

import opengate_config as conf
import requests
import uuid
import json
import sys
import getopt
import time
import datetime
import random

headers = {
    'X-ApiKey': conf.API_KEY,
    'Content-Type': 'application/json'
}


def current_milli_time():
    return long(round(time.time()))


def add_some_noise(randomize_this):
    return randomize_this + random.randint(-5, 5)


def get_device(id):

    zigbee_id = str(uuid.uuid4())
    try:
        zigbee_id_file = open('.zigbee_id', 'r')
        zigbee_id = zigbee_id_file.read().strip()
    except IOError:
        print 'Can\'t read zigbiee_id file'


    device = {
        'event': {
            'id': '{0}'.format(current_milli_time()),
            'device': {
                'id': id,
                'name': 'Virtual Device',
                'description': 'Virtual Device for Testing',
                'hardware': {
                    'serialnumber': str(uuid.uuid4()),
                    'manufacturer': {
                        'name': conf.MANUFACTURER,
                        'oui': '41-B9-72'
                    },
                    'model': {
                        'name': conf.MODEL_NAME
                    }
                },
                'softwareList': [
                    {
                        'name': 'BloodPressure',
                        'type': 'FIRMWARE',
                        'version': '1.0',
                        'date': '2012-09-11T13:02:41Z'
                    }
                ],
                'specificType': 'METER',
                'location': {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'coordinates': {
                        'latitude': 42.41675,
                        'longitude': -3.7028
                    }
                },
                'temperature': {
                    'unit': 'C',
                    'current': add_some_noise(33),
                    'status': 'NORMAL',
                    'trend': 'DECREASING',
                    'average': '20',
                    'maximum': '25',
                    'minimum': '15'
                },
                'operationalStatus': 'UP',
                'powerSupply': {
                    'source': 'BATTERY',
                    'status': 'NORMAL',
                    'batteryChargeLevel': {
                        'trend': 'EMPTY',
                        'status': 'CHARGED',
                        'percentage': add_some_noise(50)
                    }
                },
                'communicationsModules': [
                    {
                        'name': 'Bluetooth Module',
                        'type': 'Bluetooth',
                        'hardware': {
                            'serialnumber': str(uuid.uuid4()),
                            'manufacturer': {
                                'name': 'amplia)))',
                                'oui': '8C-EA-42'
                            },
                            'model': {
                                'name': 'ABT'
                            }
                        },
                        'subscription': {
                            'name': 'bluetooh_network',
                            'description': 'Bluetooth Network'
                        }
                    },
                    {
                        'id': zigbee_id,
                        'name': 'ZigBee Module',
                        'type': 'ZIGBEE',
                        'hardware': {
                            'serialnumber': '52:54:00:%02x:%02x:%02x' % (
                                random.randint(0, 255),
                                random.randint(0, 255),
                                random.randint(0, 255),
                            )
                        }
                    }
                ]
            }
        }
    }

    return device


def update(id):
    print 'Updating device {0}'.format(id)
    device_as_json = json.dumps(get_device(id), indent=2)
    print device_as_json
    ogapi_devices_uri = '{0}/devices/{1}/collect/dmm'.format(conf.OG_SOUTH_API_BASE_URI, id)
    r = requests.post(ogapi_devices_uri, data=device_as_json, headers=headers)
    print 'Status code received {}'.format(r.status_code)
    print r.text


def main():
    try:  # parse command line options
        opts, args = getopt.getopt(sys.argv[1:], 'hi:', ['help', 'identifier='])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    device_id = None
    if conf.DEFAULT_DEVICE_ID is not None:
        device_id = conf.DEFAULT_DEVICE_ID
    else:
        try:
            device_id_file = open('.device_id', 'r')
            device_id = device_id_file.read().strip()
        except IOError:
            print 'Can\'t read device_id file'

    for o, a in opts:  # process options
        if o in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif o in ('-i', '--identifier'):
            device_id = a
        else:
            print __doc__
            sys.exit(0)

    if device_id is None:
        print 'Please, provide a device identifier'
    else:
        update(device_id)


if __name__ == '__main__':
    main()
