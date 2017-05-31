#!/usr/bin/env python
'''
This module emulates a device connected to OpenGate
using MQTT protocol.
'''

import time
import random

BURST_SIZE = 5


def current_milli_time():
    '''Gets current millis'''
    return long(round(time.time()))


def add_some_noise(randomize_this):
    '''Adds some noise befor send the data'''
    return randomize_this + random.randint(1, 100)


def get_data_points(device_id):
    '''Prepare data points to send'''
    datapoints = {
        'version': '1.0.0',
        'device': device_id,
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

    return datapoints
