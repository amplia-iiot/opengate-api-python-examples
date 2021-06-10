#!/usr/bin/env python
import getopt
from ipaddress import ip_address
import json
import sys
import time

import opengate_config as conf

from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource


__author__ = 'Edu Lahe'


def current_milli_time():
    return int(round(time.time()))


def getDmmPayload(device_id):
    payload = {
        "version": "7.0",
        "event": {
            "id": '{0}'.format(current_milli_time()),
            "device": {
                "id": device_id,
                "path": [],
                "name": "my device",
                "description": "device description",
                "temperature": {
                    "unit": "C",
                    "current": "25.2",
                    "status": "NORMAL",
                    "trend": "DECREASING",
                    "average": "20",
                    "maximum": "25",
                    "minimum": "15"
                }
            }
        }
    }
    return payload


def getIotPayload(device_id):
    payload = {
        "version": "1.0.0",
        "datastreams": [{
            "id": device_id,
            "feed": "feed_1",
            "datapoints": [{
                "at": '{0}'.format(current_milli_time()),
                "value": 41
            }]
        }]
    }
    return payload


def getAlarmPayload(device_id):
    payload = {
        "event": {
            "alarm": {
                "id": '{0}'.format(current_milli_time()),
                "deviceId": device_id,
                "severity": "CRITICAL",
                "priority": "HIGH",
                "name": "Alarm_1",
                "specific": "",
                "description": "alarm description",
                "timestamp": '{0}'.format(current_milli_time()),
                "variables": [{
                    "name": "variable1",
                    "value": "value1"
                }, {
                    "name": "variable2",
                    "value": 10
                }]
            }
        }
    }
    return payload


def usage():  # pragma: no cover
    print("Options (mandatory):")
    print("\t-e, --event=\t\tEvent type: DMM|IOT|ALARM")
    print("")
    print("Example:")
    print("\tpython device_south_coap.py -e DMM")


def main():  # pragma: no cover
    server_ip = None
    server_port = None
    api_key = None
    device_id = None
    event_type = None
    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "he:", ["help", "event="])
    except getopt.GetoptError as err:
        # print(help information and exit:)
        print(str(err)  # will print something like "option -a not recognized")
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-e", "--event"):
            event_type = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit(2)

    if event_type is None:
        print("Event type must be specified")
        usage()
        sys.exit(2)

    if conf.COAP_SERVER_IP is not None:
        server_ip = conf.COAP_SERVER_IP
    else:
        server_ip = "127.0.0.1"
        print('Can\'t read COAP_SERVER_IP from opengate_config.py using default value ' + server_ip)

    if conf.COAP_SERVER_PORT is not None:
        server_port = conf.COAP_SERVER_PORT
    else:
        server_port = 56830
        print('Can\'t read COAP_SERVER_IP from opengate_config.py using default value ' + str(server_port))

    if conf.API_KEY is not None:
        api_key = conf.API_KEY
    else:
        print('Can\'t read API_KEY from opengate_config.py')
        sys.exit(2)

    if conf.DEFAULT_DEVICE_ID is not None:
        device_id = conf.DEFAULT_DEVICE_ID
    else:
        try:
            DEVICE_ID_FILE = open('.device_id', 'r')
            device_id = DEVICE_ID_FILE.read().strip()
        except IOError:
            print('Can\'t read device_id file neither from .device_id file nor opengate_config.py')
            sys.exit(2)

    path = "v70/devices/"
    payload = None
    command = coap.POST
    if event_type == "DMM":
        path = path + "collect/dmm"
        payload = json.dumps(getDmmPayload(device_id), indent=2)
    elif event_type == "IOT":
        path = path + "collect/iot"
        payload = json.dumps(getIotPayload(device_id), indent=2)
    elif event_type == "ALARM":
        path = path + "events/alarms"
        payload = json.dumps(getAlarmPayload(device_id), indent=2)
    elif event_type == "TEST":
        path = path + "test"
        command = coap.GET
    else:
        print("Event type " + event_type + " not recognized")
        usage()
        sys.exit(2)

    reactor.callLater(1, requestResource, protocol, command, server_ip, server_port, api_key, path, payload, device_id)

    reactor.listenUDP(61617, protocol)  # , interface="::")
    reactor.run()


def requestResource(protocol, command, server_ip, server_port, api_key, path, payload, device_id):

    request = coap.Message(code=command)
    request.opt.uri_path = (path.split("/"))
    request.opt.observe = 0
    # api-key option
    request.opt.addOption(coap.StringOption(number=2502, value=api_key))
    # device id option
    request.opt.addOption(coap.StringOption(number=2503, value=device_id))
    # version option (reserved for future requirements)
#    request.opt.addOption(coap.StringOption(number=2504, value="1.0"))
    print('Remote server in ' + server_ip + ':' + str(server_port))
    request.remote = (ip_address(server_ip), server_port)
    if payload != None:
        request.payload = str(payload)
        request.opt.content_format = coap.media_types_rev['application/json']
    print("About to send payload: " + request.payload + " of type " + str(type(request.payload)))
    d = protocol.request(request, observeCallback=printLaterResponse)
    d.addCallback(printResponse)
    d.addErrback(noResponse)

def printResponse(response):
    print('First result: ' + response.payload)
    reactor.stop()

def printLaterResponse(response):
    print('Observe result: ' + response.payload)

def noResponse(failure):
    print('Failed to fetch resource:')
    print(failure)
    reactor.stop()

if __name__ == '__main__':  # pragma: no cover
    log.startLogging(sys.stdout)
    main()
