#!/usr/bin/env python
'''
device_south_iot.py [-options]
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


def get_data_points():
    device = {
        'version': '1.0.0',
        'datastreams': [
            {
                'id': 'health.glucose.concentration',
                'feed': 'health',
                'datapoints': [
                    {'at': current_milli_time(), 'value': 200}
                ]
            },
            {
                'id': 'health.bodycomposition.weight',
                'feed': 'health',
                'datapoints': [
                    {'at': current_milli_time(), 'value': 12.56}
                ]
            },
            {
                'id': 'health.bloodpresure.pulserate',
                'feed': 'health',
                'datapoints': [
                    {'at': current_milli_time(), 'value': 62}
                ]
            },
            {
                'id': 'health.bloodpresure.systolic',
                'feed': 'health',
                'datapoints': [
                    {'at': current_milli_time(), 'value': 62}
                ]
            }
        ]
    }

    return device


def update(id):
    print 'Sending IoT data {0}'.format(id)
    device_as_json = json.dumps(get_data_points())
    print device_as_json
    ogapi_devices_uri = '{0}/devices/{1}/collect/iot'.format(conf.OG_SOUTH_API_BASE_URI, id)
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
