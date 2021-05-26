#!/usr/bin/env python
'''
device_north_crud.py [-options]
Options:
-h, --help
-c, --create
-r, --read=deviceid
-u, --update=deviceid
-d, --delete=deviceid
-t, --trusted Enable trusted boot
-i, --deviceid=deviceid Create with custom device id
'''

import random
import hashlib
import requests
import uuid
import json
import sys
import getopt
import opengate_config as conf

ogapi_devices_uri = '{0}/provision/organizations/{1}/devices'.format(
    conf.OG_NORTH_API_BASE_URI,
    conf.ORGANIZATION)

ogapi_wifi_uri = '{0}/provision/organizations/{1}/subscriptions'.format(
    conf.OG_NORTH_API_BASE_URI,
    conf.ORGANIZATION)
ogapi_comm_modules_uri = '{0}/provision/organizations/{1}/entities/communicationsModules'.format(
    conf.OG_NORTH_API_BASE_URI,
    conf.ORGANIZATION)

ogapi_relation_uri = '{0}/provision/organizations/{1}/entities/relations'.format(
    conf.OG_NORTH_API_BASE_URI,
    conf.ORGANIZATION)


def get_device(id, trusted_boot=False, serial=None):

    device = {
        'provision': {
            'administration': {
		'channel': {
	            '_current': { 'value': conf.CHANNEL }
       		 },
          	'serviceGroup': {
                    '_current': { 'value': conf.SERVICE_GROUP }
         	 }
	    },
            'device': {
		'identifier': {
	            '_current': { 'value': id }
       		   },
          	'name': {
            	    '_current': { 'value': id }
	          },
          	'specificType': {
	            '_current': { 'value': 'CONCENTRATOR' }
          	},
          	'description': {
	            '_current': { 'value': 'Device for testing purposes' }
          	}
            }
        }
    }

    if trusted_boot:
        hasher = hashlib.sha256()
        with open(conf.FIRMWARE_FILE_NAME, 'rb') as device_firmware:
            buf = device_firmware.read()
            hasher.update(buf)

        trusted_boot_hash = hasher.hexdigest()
        device['device']['provision']['trustedBoot'] = trusted_boot_hash

    if serial is not None:
        serials = [serial]
        device['device']['provision']['serialNumber'] = serials

    return device


def get_wifi_interface(wifi_id):
    wifi_interface = {
        'subscription': {
            'id': wifi_id,
            'provision': {
                'customId': [wifi_id],
                'template': 'default',
                'name': [wifi_id],
                'specificType': ['WIFI'],
                'description': ['Wi-Fi subscription for testing'],
                'admin': {
                    'organization': conf.ORGANIZATION,
                    'channel': conf.CHANNEL,
                    'administrativeState': 'ACTIVE',
                    'serviceGroup': conf.SERVICE_GROUP
                },
                'address': [
                    {
                        'type': 'IPV4',
                        'value': '217.126.182.38',
                        'apn': 'kontron'
                    }
                ]
            }
        }
    }

    return wifi_interface


def get_zigbee_communication_module(zigbee_id):
    zigbee_interface = {
        'communicationsModule': {
            'id': zigbee_id,
            'provision': {
                'customId': [zigbee_id],
                'template': 'default',
                'specificType': ['ZIGBEE'],
                'name': [zigbee_id],
                'description': ['ZigBee communications module for testing'],
                'admin': {
                    'organization': conf.ORGANIZATION,
                    'channel': conf.CHANNEL,
                    'administrativeState': 'ACTIVE',
                    'serviceGroup': conf.SERVICE_GROUP
                },
                'mac': [
                    '52:54:00:%02x:%02x:%02x' % (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                    )
                ]
            }
        }
    }

    return zigbee_interface


def get_relations(device_id, wifi_id, zigbee_id):
    relation = {
        'relation': {
            'template': 'default',
            'links': [
                {'entityType': 'DEVICE', 'id': device_id},
                {'entityType': 'SUBSCRIPTION', 'id': wifi_id},
                {'entityType': 'COMMUNICATIONS_MODULE', 'id': zigbee_id}
            ]
        }
    }

    return relation


def http_post(entity_type, entity_id, entity_as_json, entity_uri):
    print('Creating {0} {1}'.format(entity_type, entity_id))
    print(entity_as_json)
    r = requests.post(entity_uri, data=entity_as_json, headers=conf.HEADERS)
    print('Status code received {0}'.format(r.status_code))
    try:
        # Try to print(JSON response)
        print(json.dumps(r.json(), indent=2))
    except:
        pass # Do nothing if JSON can't be dumped

    if r.status_code != 201:
        raise AssertionError('Assertion error, status code %s is different to 201' % r.status_code)

    # A file with the entity id is create for further DMM & IoT operations
    # See device_south_dmm.py & device_south_iot.py
    try:
        entity_id_file = open('.{0}_id'.format(entity_type), 'w')
        entity_id_file.write(entity_id)
    except IOError:
        print('Can\'t create {0} file'.format(entity_type))


def create(device_id=None, trusted_boot=False):
    try:
        if device_id is None:
            device_id = str(uuid.uuid4())
        device_as_json = json.dumps(get_device(device_id, trusted_boot), indent=2)
        http_post('device', device_id, device_as_json, ogapi_devices_uri)

        wifi_id = str(uuid.uuid4())
        wifi_as_json = json.dumps(get_wifi_interface(wifi_id), indent=2)
        http_post('wifi', wifi_id, wifi_as_json, ogapi_wifi_uri)

        zigbee_id = str(uuid.uuid4())
        zigbee_as_json = json.dumps(get_zigbee_communication_module(zigbee_id), indent=2)
        http_post('zigbee', zigbee_id, zigbee_as_json, ogapi_comm_modules_uri)

        relation_as_json = json.dumps(get_relations(device_id, wifi_id, zigbee_id), indent=2)
        http_post('relation', device_id, relation_as_json, '{0}?action=CREATE'.format(ogapi_relation_uri))
    except Exception as e:
        print(e)

def read(dev_id, wifi_id=None):
    print('Reading device {0}'.format(dev_id))
    uri = '{0}/{1}'.format(ogapi_devices_uri, dev_id)
    r = requests.get(uri, headers=conf.HEADERS)
    print('Status code received {}'.format(r.status_code))
    if r.status_code == 200:
        print(json.dumps(json.loads(r.text), indent=2))

    print('Reading wi-fi {0}'.format(wifi_id))
    uri = '{0}/{1}'.format(ogapi_wifi_uri, wifi_id)
    r = requests.get(uri, headers=conf.HEADERS)
    print('Status code received {}'.format(r.status_code))
    if r.status_code == 200:
        print(json.dumps(json.loads(r.text), indent=2))


def update(dev_id, serial):
    print('Updating device {0}'.format(dev_id))
    device_as_json = json.dumps(get_device(dev_id, serial=serial), indent=2)
    print(device_as_json)
    uri = '{0}/{1}'.format(ogapi_devices_uri, dev_id)
    r = requests.put(uri, data=device_as_json, headers=conf.HEADERS)
    print('Status code received {}'.format(r.status_code))
    print(r.text)


def delete(dev_id, wifi_id=None):
    # Relation between device and wi-fi module is automatically removed when device or wi-fi is deleted
    if wifi_id is not None:
        print('Deleting wi-fi {0}'.format(wifi_id))
        uri = '{0}/{1}'.format(ogapi_wifi_uri, wifi_id)
        r = requests.delete(uri, headers=conf.HEADERS)
        print('Status code received {}'.format(r.status_code))
        print(r.text)

    print('Deleting device {0}'.format(dev_id))
    uri = '{0}/{1}'.format(ogapi_devices_uri, dev_id)
    r = requests.delete(uri, headers=conf.HEADERS)
    print('Status code received {}'.format(r.status_code))
    print(r.text)


def load_ids():
    device_id = None
    wifi_id = None

    if conf.DEFAULT_DEVICE_ID is not None:
        device_id = conf.DEFAULT_DEVICE_ID
    else:
        try:
            device_id_file = open('.device_id', 'r')
            device_id = device_id_file.read().strip()
        except IOError:
            print('Can\'t read device_id file')

    if conf.DEFAULT_WIFI_ID is not None:
        wifi_id = conf.DEFAULT_WIFI_ID
    else:
        try:
            wifi_id_file = open('.wifi_id', 'r')
            wifi_id = wifi_id_file.read().strip()
        except IOError:
            print('Can\'t read device_id file')

    return device_id, wifi_id


def main():
    try:  # parse command line options
        opts, args = getopt.getopt(sys.argv[1:], 'hcrudti:', ['help', 'create', 'read', 'update', 'delete', 'trusted', 'deviceid'])
    except getopt.error as msg:
        print(msg)
        print('for help use --help')
        sys.exit(2)

    if len(opts) == 0:
        print(__doc__)
        sys.exit(0)

    box_ids = load_ids()

    for o, a in opts:  # process options
        if o in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        elif o in ('-c', '--create'):
            create()
        elif o in ('-r', '--read'):
            read(box_ids[0], box_ids[1])
        elif o in ('-u', '--update'):
            update(box_ids[0], a)
        elif o in ('-d', '--delete'):
            delete(box_ids[0], box_ids[1])
        elif o in ('-t', '--trusted'):
            create(trusted_boot=True)
        elif o in ('-i', '--deviceid'):
            create(a)
        else:
            print(__doc__)
            sys.exit(0)


if __name__ == '__main__':
    main()
