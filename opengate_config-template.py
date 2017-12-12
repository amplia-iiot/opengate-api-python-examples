'''
Configuration file for OpenGate Python Examples
'''
OPENGATE_HOST = 'api.opengate.es'
NORTH_PORT = 80
SOUTH_PORT = 80
SOUTH_WEBSOCKET_PORT = SOUTH_PORT
SOUTH_MQTT_PORT = 1883
OG_NORTH_API_BASE_URI = 'http://{0}:{1}/north/v80'.format(
    OPENGATE_HOST, NORTH_PORT)
OG_SOUTH_API_BASE_URI = 'http://{0}:{1}/south/v80'.format(
    OPENGATE_HOST, SOUTH_PORT)
OG_SOUTH_WEBSOCKET_BASE_URI = 'ws://{0}:{1}/south/v70/sessions'.format(
    OPENGATE_HOST, SOUTH_WEBSOCKET_PORT)
ORGANIZATION = 'your-organization'
CHANNEL = 'default_channel'
SERVICE_GROUP = 'emptyServiceGroup'
API_KEY = 'your-apikey'

HEADERS = {
    'X-ApiKey': API_KEY,
    'Content-Type': 'application/json'
}
DEFAULT_DEVICE_ID = None
DEFAULT_WIFI_ID = None
BUNDLE_NAME = 'test-bundle-20170529'
BUNDLE_VERSION = '0.0.0'
MANUFACTURER = 'Test-Manufacturer'
MODEL_NAME = 'Virtual-Test-Device'
#################################################
