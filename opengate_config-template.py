OPENGATE_HOST = 'cloud.opengate.es'
NORTH_PORT = 25281
SOUTH_PORT = 9955
SOUTH_WEBSOCKET_PORT = 9956
OG_NORTH_API_BASE_URI = 'http://{0}:{1}/v70'.format(OPENGATE_HOST, NORTH_PORT)
OG_SOUTH_API_BASE_URI = 'http://{0}:{1}/v70'.format(OPENGATE_HOST, SOUTH_PORT)
OG_SOUTH_WEBSOCKET_BASE_URI = 'ws://{0}:{1}/v70'.format(OPENGATE_HOST, SOUTH_WEBSOCKET_PORT)
ORGANIZATION = 'your_organization'
CHANNEL = 'default_channel'
API_KEY = 'your_api_key'
HEADERS = {
    'X-ApiKey': API_KEY,
    'Content-Type': 'application/json'
}
DEFAULT_DEVICE_ID = None
DEFAULT_WIFI_ID = None
BUNDLE_NAME = 'test-bundle-may'
BUNDLE_VERSION = '0.0.2'
MANUFACTURER = 'Test-Manufacturer'
MODEL_NAME = 'Virtual-Test-Device'
#################################################
