#!/usr/bin/env python
'''
device_south_iot.py [-options]
Options:
-h, --help
-i, --identifier=deviceid
'''

import getopt
import json
import random
import sys
import time

import requests

import opengate_config as conf
import device_south_iot_common


def update(device_id):
    '''Sends data points'''
    print 'Sending a burst of {0} request'.format(device_south_iot_common.BURST_SIZE)
    for i in range(device_south_iot_common.BURST_SIZE):
        print 'Sending packet {0} IoT data from {1}'.format(i, device_id)
        device_as_json = json.dumps(
            device_south_iot_common.get_data_points(device_id), indent=2)
        print device_as_json
        ogapi_devices_uri = '{0}/devices/{1}/collect/iot'\
            .format(conf.OG_SOUTH_API_BASE_URI, device_id)
        response = requests.post(ogapi_devices_uri, data=device_as_json,
                                 headers=conf.HEADERS)
        print 'Status code received {}'.format(response.status_code)
        print response.text
        time.sleep(1)


def main():
    '''Main function'''
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

    for option, argument in opts:  # process options
        if option in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif option in ('-i', '--identifier'):
            device_id = argument
        else:
            print __doc__
            sys.exit(0)

    if device_id is None:
        print 'Please, provide a device identifier'
    else:
        update(device_id)


if __name__ == '__main__':
    main()
