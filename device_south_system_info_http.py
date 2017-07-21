#!/usr/bin/env python
'''This module emulates a device that sends information about system
utilization connected to OpenGate using HTTP protocol.

Usage: device_south_system_info_http.py [OPTIONS]...

Option
 -h\t--help
 -i\t--identifier=deviceid
 -n\t--number-of-datastreams=max_datastreams\tMax number of datastreams to send.
'''

import sys
import getopt
import psutil
import json
import requests
import time
import random

import opengate_config as conf
import device_south_iot_common as common

def percent_description(x):
    if x > 100 or x < 0: return 'INVALID'
    if x == 100: return 'MAX'
    if x >= 80: return 'VERY HIGH'
    if x >= 60: return 'HIGH'
    if x >= 40: return 'MEDIUM'
    if x >= 20: return 'LOW'
    if x > 0: return 'VERY LOW'
    else: return 'MIN'

def get_system_data_points(device_id):
    '''Prepare system utilization data points to send'''
    now = common.current_milli_time()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    io = psutil.disk_io_counters()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    return {
        'version': '1.0.0',
        'device': device_id,
        'datastreams': [
            {
                'id': 'device.dmm.ram.total',
                'datapoints': [
                    {
                        'at': now,
                        'value': mem.total / 1000000
                    }
                ]
            },
            {
                'id': 'device.dmm.ram.usage',
                'datapoints': [
                    {
                        'at': now,
                        'value': mem.percent
                    }
                ]
            },
            {
                'id': 'uptime',
                'datapoints': [
                    {
                        'at': now,
                        'value': now - psutil.boot_time()
                    }
                ]
            },
            {
                'id': 'device.dmm.cpu',
                'datapoints': [
                    {
                        'at': now,
                        'value': cpu_percent
                    }
                ]
            },
            {
                'id': 'cpufreq',
                'datapoints': [
                    {
                        'at': now,
                        'value': psutil.cpu_freq()[0]
                    }
                ]
            },
            {
                'id': 'swaptotal',
                'datapoints': [
                    {
                        'at': now,
                        'value': swap.total / 1000000
                    }
                ]
            },
            {
                'id': 'swapusage',
                'datapoints': [
                    {
                        'at': now,
                        'value': swap.percent
                    }
                ]
            },
            {
                'id': 'device.dmm.nonVolatilStorage.usage',
                'datapoints': [
                    {
                        'at': now,
                        'value': psutil.disk_usage('/').percent
                    }
                ]
            },
            {
                'id': 'diskread',
                'datapoints': [
                    {
                        'at': now,
                        'value': io.read_bytes / 1000000
                    }
                ]
            },
            {
                'id': 'diskwrite',
                'datapoints': [
                    {
                        'at': now,
                        'value': io.write_bytes / 1000000
                    }
                ]
            },
            {
                'id': 'cpuload',
                'datapoints': [
                    {
                        'at': now,
                        'value': percent_description(cpu_percent)
                    }
                ]
            }
        ]
    }

def update(device_id, dry_run, max_datastreams):
    '''Generates message with data points and sends it'''
    message = get_system_data_points(device_id)
    if max_datastreams is not None:
        while len(message['datastreams']) > max_datastreams:
            del message['datastreams'][random.randint(0, len(message['datastreams']) - 1)]
    device_as_json = json.dumps(message, indent=2)
    print device_as_json
    if not dry_run:
        print 'Sending packet as {0}'.format(device_id)
        ogapi_devices_uri = '{0}/devices/{1}/collect/iot'\
            .format(conf.OG_SOUTH_API_BASE_URI, device_id)
        response = requests.post(ogapi_devices_uri, data=device_as_json,
                                 headers=conf.HEADERS)
        print 'Status code received {}'.format(response.status_code)
        print response.text

def main():
    try: # parse command line options
        opts, args = getopt.getopt(sys.argv[1:], 'hi:n:', ['help', 'identifier=', 'number-of-datastreams=', 'dry-run'])
    except getopt.error, msg:
        print msg
        print 'For help use --help'
        sys.exit(2)

    device_id = None
    dry_run = False
    max_datastreams = None
    if conf.DEFAULT_DEVICE_ID is not None:
        device_id = conf.DEFAULT_DEVICE_ID
    else:
        try:
            device_id_file = open('.device_id', 'r')
            device_id = device_id_file.read().strip()
        except IOError:
            print 'Can\'t read device_id file'

    for option, argument in opts: # process options
        if option in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif option in ('-i', '--identifier'):
            device_id = argument
            print 'Using device id: ' + device_id
        elif option in ('-n', '--number-of-datastreams'):
            max_datastreams = int(argument)
            print 'Sending a maximum of {0} datapoints'.format(max_datastreams)
        elif option in ('--dry-run'):
            dry_run = True
            print 'Executing without sending message'
        else:
            print __doc__
            sys.exit(0)

    if device_id is None:
        print 'Please, provide a device identifier'
    else:
        update(device_id, dry_run, max_datastreams)

if __name__ == '__main__':
    main()
