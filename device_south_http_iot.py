#!/usr/bin/env python
'''
device_south_iot.py [-options]
Options:
-h, --help
-i, --identifier=deviceid
'''

import opengate_config as conf
import requests
import json
import sys
import getopt
import time
import random


def current_milli_time():
    return long(round(time.time()))


burst_size = 5


def add_some_noise(randomize_this):
    return randomize_this + random.randint(1, 100)


def get_data_points():
    device = {
        'version': '1.0.0',
        'datastreams': [
            {
                'id': 'health.glucose.concentration',
                'datapoints': [
                    {'at': current_milli_time(), 'value': add_some_noise(201)}
                ]
            },
            {
                'id': 'health.bodycomposition.weight',
                'datapoints': [
                    {'at': current_milli_time(), 'value': add_some_noise(71.5)}
                ]
            },
            {
                'id': 'health.bloodpresure.pulserate',
                'datapoints': [
                    {'at': current_milli_time(), 'value': add_some_noise(76)}
                ]
            },
            {
                'id': 'health.bloodpresure.systolic',
                'datapoints': [
                    {'at': current_milli_time(), 'value': add_some_noise(69)}
                ]
            }
        ]
    }

    return device


def update(id):
    print 'Sending a burst of {0} request'.format(burst_size)
    for i in range(burst_size):
        print 'Sending IoT data {0}'.format(id)
        device_as_json = json.dumps(get_data_points(), indent=2)
        print device_as_json
        ogapi_devices_uri = '{0}/devices/{1}/collect/iot'\
            .format(conf.OG_SOUTH_API_BASE_URI, id)
        r = requests.post(ogapi_devices_uri, data=device_as_json,
                          headers=conf.HEADERS)
        print 'Status code received {}'.format(r.status_code)
        print r.text
        time.sleep(1)


def main():
    try:  # parse command line options
        long_option_list = ['help', 'identifier=']
        opts, args = getopt.getopt(sys.argv[1:], 'hi:', long_option_list)
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
