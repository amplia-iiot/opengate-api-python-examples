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

current_milli_time = lambda: int(round(time.time() * 1000))

headers = {
    'X-ApiKey': conf.API_KEY,
    'Content-Type': 'application/json'
}


def get_device(id):
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
                        'name': 'amplia)))',
                        'oui': '41-B9-72'
                    },
                    'model': {
                        'name': 'BloodPressure'
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
                        'latitude': 42.41677,
                        'longitude': -3.7028
                    }
                },
                'temperature': {
                    'unit': 'C',
                    'current': '33',
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
                        'percentage': '50'
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
                    }
                ]
            }
        }
    }

    return device


def update(id):
    print 'Updating device {0}'.format(id)
    device_as_json = json.dumps(get_device(id))
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

    device_id = conf.DEFAULT_DEVICE_ID

    for o, a in opts:  # process options
        if o in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif o in ('-i', '--identifier'):
            device_id = a
        else:
            print __doc__
            sys.exit(0)

    update(device_id)


if __name__ == '__main__':
    main()
