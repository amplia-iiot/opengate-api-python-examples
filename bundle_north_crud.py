#!/usr/bin/env python
'''
device_north_crud.py [-options]
Options:
-h, --help
-c, --create
-r, --read=deviceid
-u, --update=deviceid
-d, --delete=deviceid
'''

import sys
import json
import getopt
import opengate_config as conf
import requests

ogapi_bundles_uri = '{0}/provision/bundles'.format(conf.OG_NORTH_API_BASE_URI)

ogapi_bundle_uri = '{0}/{1}/versions/{2}'.format(
    ogapi_bundles_uri, conf.BUNDLE_NAME, conf.BUNDLE_VERSION)

ogapi_deployment_elements_uri = '{0}/deploymentElements'.format(
    ogapi_bundle_uri)

ogapi_search_catalog_hardware = '{0}/search/catalog/hardwares'.format(
    conf.OG_NORTH_API_BASE_URI)

headers = {
    'X-ApiKey': conf.API_KEY,
    'Content-Type': 'application/json'
}


def create_bundle():
    ''' Creates a software bundle based on device the model name
    from configuration. It performs a searching on the hardaware
    catalog API
    '''
    print 'Getting model ID, searching on hardware catalog API...'
    search_filter = {
        'filter': {
            'eq': {
                'modelName': conf.MODEL_NAME
            }
        }
    }
    search_filter_as_json = json.dumps(search_filter, indent=2)
    print search_filter_as_json

    response = requests.post(ogapi_search_catalog_hardware,
                             data=search_filter_as_json, headers=headers)

    if response.status_code == 200:
        search_response = response.json()
        search_response_as_json = json.dumps(search_response, indent=2)
        print search_response_as_json

        hardware_id = None
        # It's supposed that there will be only one manufacturer for
        # the providel model so we can safely perform `search_response['manufacturer'][0]`
        for model in search_response['manufacturer'][0]['models']:
            if model['name'] == conf.MODEL_NAME:
                hardware_id = model['id']

        print 'Hardware ID got {}'.format(hardware_id)

        bundle = {
            'bundle': {
                'name': conf.BUNDLE_NAME,
                'version': conf.BUNDLE_VERSION,
                'description': 'Test Bundle',
                'userNotes': 'Some comments',
                'workgroup': conf.ORGANIZATION,
                'preaction': ['COMMS_DOWN'],
                'postaction': ['HARDWARE_RESET'],
                'hardware': hardware_id
            }
        }

        bundle_as_json = json.dumps(bundle, indent=2)
        print 'Creating bundle on {0}'.format(ogapi_bundles_uri)
        print bundle_as_json
        response = requests.post(
            ogapi_bundles_uri, data=bundle_as_json, headers=headers)
        print 'Status code received {}'.format(response.status_code)
        print response.content
        if response.status_code == 201:
            bundle_location = response.headers['Location']
            print 'Bundle location {0}'.format(bundle_location)

    else:
        print 'Device not found for model {0}'.format(conf.MODEL_NAME)


def create_deployment_element():
    '''Creates a deployment element for a bundle
    '''
    deployment_element_file_name = conf.FIRMWARE_FILE_NAME

    deployment_element = {
        'deploymentElement': {
            'name': '{0}-deployment-element-1'.format(conf.BUNDLE_NAME),
            'version': conf.BUNDLE_VERSION,
            'type': 'FIRMWARE',
            'path': 'from-opengate-{0}'.format(deployment_element_file_name),
            'order': '1',
            'operation': 'INSTALL',
            'option': 'MANDATORY',
            'validators': [
                {
                    'type': 'SHA-256',
                    'mode': 'SECURE_BOOT'
                }
            ]
        }
    }

    deployment_element_as_json = json.dumps(deployment_element, indent=2)

    files = {
        'meta': (
            'meta',
            deployment_element_as_json,
            'application/json',
            {'Expires': '0'}
        ),
        'file': (
            'file',
            open(deployment_element_file_name, 'rb'),
            'application/text',
            {'Expires': '0'}),
    }

    print 'Creating deployment element on {0}'.format(ogapi_deployment_elements_uri)
    print deployment_element_as_json

    response = requests.post(ogapi_deployment_elements_uri,
                             files=files, headers={'X-ApiKey': conf.API_KEY})
    print 'Status code received {}'.format(response.status_code)
    print response.content


def bundle_activation(state):
    '''Activates the bundle to enable its use
    '''
    bundle = {
        'bundle': {
            'active': state
        }
    }
    bundle_as_json = json.dumps(bundle, indent=2)
    print 'Setting bundle activation to {0} on {1}'.format(state, ogapi_bundle_uri)
    print bundle_as_json
    response = requests.put(
        ogapi_bundle_uri, data=bundle_as_json, headers=headers)
    print 'Status code received {}'.format(response.status_code)
    print response.content


def create():
    '''Drives the bundle creation
    * First, create the bundle
    * Sencond, add a deployment element to the just created bundle
    * Third, activates the bundle, thus it can be used on update operations
    '''
    create_bundle()
    create_deployment_element()
    bundle_activation(True)


def delete():
    '''Deletes a bundle
    Note:
    Attention, if you use a bundle in an update operation, then it can't be deleted
    '''

    bundle_activation(False)

    print 'Deleting bundle {0}'.format(ogapi_bundle_uri)
    response = requests.delete(ogapi_bundle_uri, headers=headers)
    print 'Status code received {}'.format(response.status_code)
    print response.content


def main():
    '''Main function of the script
    '''
    try:  # parse command line options
        opts, args = getopt.getopt(sys.argv[1:], 'hcad', [
                                   'help', 'create', 'activate', 'deactivate'])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    if len(opts) is 0:
        print __doc__
        sys.exit(0)

    for option, argument in opts:  # process options
        if option in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif option in ('-c', '--create'):
            create()
        elif option in ('-d', '--delete'):
            delete()
        elif option in ('-a', '--activate'):
            bundle_activation(True)
        elif option in ('-t', '--deactivate'):
            bundle_activation(False)
        else:
            print __doc__
            sys.exit(0)


if __name__ == '__main__':
    main()
