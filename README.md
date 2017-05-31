# OpenGate API Python examples
Here you can find some simple OpenGate REST APIs examples written in Python.

## Quick start 
In order to use these scripts you must:

1. Rename the python file `opengate_config_template.py` to `opengate_config.py`.
2. Setup the configuration parameters with your specific data.
3. Install the required dependencies:

### Dependencies 
You can install the required dependencies using [`pip`](https://pypi.python.org/pypi/pip) and the provided `requirements.txt` file.

```
pip install -r requirements.txt
```

## North API Interface Features
All the tasks shown here can be done using the OpenGate Web interface, however, sometimes it's needed a programmatic way of integration that can be done through the OpenGate API.

### Provision
The script `device_north_crud.py` is able to perform some basic CRUD operations using the OpenGate North API.

#### Creation

Using the `-c` option the script creates a device, some communication modules and the relationship between all of them. Please take care of the data into the script, it contains some important info, for example, the public IP exposed to accept incoming operations from OpenGate if you're planning to use an HTTP in your device. In this simple example, the IP information is on the Wi-Fi communications module. This IP will be used by OpenGate to send operation requests like reboot equipment or software update. So please, set up your IP info correctly if you want to receive operations from OpenGate exposing an HTTP server.

**Important**: The script performs some basic caching on the device, Wi-If and relation ids for further operations
(delete, update, read). The id information is stored on disk in the following hidden (in Unix/Linux) files:
`.device_id`, `.wifi_id`, etc. You can override the cached IDs using the following configuration
parameters:

* `DEFAULT_DEVICE_ID`
* `DEFAULT_WIFI_ID`

#### Read
Using `-r` option the script reads device and communication modules info from OpenGate using the cached IDs or the default ids from the configuration file.

####  Update
Using `-u` option the current version is able to update device info, please change desired the data in the template dictionary into the script.

#### Delete
Using `-d` option the script deletes the device and related from OpenGate using the cached IDs or the default ids from the configuration.

### Operations
The script `device_north_operations.py` have some examples of operation sending to the devices with OpenGate. 

The device ID is got from the configuration file of the ID cached in the `.device_id` hidden file.

#### Reboot operation
Using the `-r` option the script sends a reboot operation to the device.

#### Update software operation
Using the `-u` option the script sends a software update operation to the device. Before performing any update a software bundle must be created. The OpenGate Web interface have a guided wizard for the bundle creation process, if you prefer the programmatic way the script `bundle_north_crud.py` helps with the bundle creation task.

## South interfaces

### HTTP
#### DMM
The script `device_south_dmm.py` sends DMM data throught the HTTP OpenGate connector.
#### Iot
The script `device_south_iot_http.py` sends a burst of IoT data throught the HTTP OpenGate connector.

### MQTT
The script `device_south_iot_mqtt.py` connects to the MQTT OpenGate connector and sends a burst of IoT data.

## Emulators
The following scripts emulate the reception and response of operations coming from OpenGate:

* `device_emulator_http_server.py`
* `device_emulator_mqtt_server.py`
* `device_emulator_websocket_server.py`