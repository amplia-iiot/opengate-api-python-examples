import time
from time import sleep
from threading import Thread
import requests
import opengate_config as conf


def operation_step_response(content, name, result, close_operation):
    '''Setup operation step response
    '''
    operation_name = content['operation']['request']['name']
    operation_id = content['operation']['request']['id']
    step_response = {
        'version': '7.0',
        'operation': {
            'response': {
                'timestamp': int(round(time.time() * 1000)),
                'name': operation_name,
                'id': operation_id,
                'variableList': [],
                'steps': [
                    {
                        'name': name,
                        'title': name,
                        'description': name,
                        'result': result
                    }
                ]
            }
        }
    }

    if close_operation:
        step_response['operation']['response']['resultCode'] = result
        step_response['operation']['response']['resultDescription'] = result

    return step_response


def multi_step_response(content, device_id, publish_operation_step_response):
    '''Emulating multi step response
    '''
    # Wait 2 seconds before start the file download operation
    sleep(2)
    print 'Multi-step response process'

    parameters = content['operation']['request']['parameters']
    download_status = None
    for parameter in parameters:
        if parameter['name'] == 'deploymentElements':
            deployment_elements = parameter['value']['array']
            for deployment_element in deployment_elements:
                download_url = deployment_element['downloadUrl']
                file_path = deployment_element['path']

                publish_operation_step_response(
                    content, device_id, 'DOWNLOADFILE', 'SUCCESSFUL', False)
                sleep(2)

                print 'Downloading {0}...'.format(download_url)
                response = requests.get(
                    download_url, headers=conf.HEADERS, stream=True)
                print 'Status code received {}'.format(response.status_code)
                if response.status_code == 200:
                    print 'Writing file to disk...'
                    with open(file_path, 'wb') as downloading_file:
                        for chunk in response:
                            downloading_file.write(chunk)

                    publish_operation_step_response(
                        content, device_id, 'ENDINSTALL', 'SUCCESSFUL', False)
                    download_status = 'SUCCESSFUL'
                    print '...done'
                    sleep(2)

                else:
                    publish_operation_step_response(
                        content, device_id, 'DOWNLOADFILE', 'ERROR', False)
                    download_status = 'ERROR'
                    print 'Something went wrong downloading file'
                    sleep(2)

    publish_operation_step_response(
        content, device_id, 'ENDUPDATE', download_status, True)


def reboot(content, device_id):
    '''REBOOT_EQUIPMENT response emulation'''

    print 'Simulating the reboot of the equipment'
    operation_id = content['operation']['request']['id']
    response = {
        'version': '7.0',
        'operation': {
            'response': {
                'deviceId': device_id,
                'timestamp': int(round(time.time() * 1000)),
                'name': 'REBOOT_EQUIPMENT',
                'id': operation_id,
                'resultCode': 'SUCCESSFUL',
                'resultDescription': 'Success',
                'steps': [
                    {
                        'name': 'REBOOT_EQUIPMENT',
                        'timestamp': int(round(time.time() * 1000)),
                        'result': 'SUCCESSFUL',
                        'description': 'Hardware reboot Ok',
                        'response': [
                            {
                                'name': 'responseParamName',
                                'value': 'responseParamValue'
                            }
                        ]
                    }
                ]
            }
        }
    }
    return response


def update(content, device_id, publish_operation_step_response):
    '''Update response emulation'''

    thread = Thread(target=multi_step_response,
                    args=(content, device_id, publish_operation_step_response,))
    thread.start()

    operation_id = content['operation']['request']['id']
    response = {
        'version': '7.0',
        'operation': {
            'response': {
                'timestamp': int(round(time.time() * 1000)),
                'name': 'UPDATE',
                'id': operation_id,
                'variableList': [],
                'steps': [
                    {
                        'name': 'BEGINUPDATE',
                        'title': 'Begin Update',
                        'description': '',
                        'result': 'SUCCESSFUL'
                    }
                ]
            }
        }
    }
    return response
