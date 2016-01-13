# OpenGate API Python examples

Here you can find some simple OpenGate REST APIs examples writen in Python.

## Quick start 

In order to use these scripts you must:

1. Rename the python file `opengate_config_template.py` to `opengate_config.py`.
2. Setup the configuration parameters with your specific data.
3. Install the required dependencies:

### Dependencies 

* [Flask](http://flask.pocoo.org/)
* [requests](http://docs.python-requests.org/en/latest/)

The recommended way to install the dependencies is using [`pip`](https://pypi.python.org/pypi/pip).
Here you have the commands to install it.

```
sudo pip install request
sudo pip install Flask
```

## North API Interface Features

The script is able to perform some basic CRUD operations using the OpenGate North API.

### Creation

Using the `-c` option the script creates a device, a wi-fi module and the relationship between them.
Please take care of the data into the script, it contains some important info, for example the public IP exposed to
accept incoming operations from OpenGate. In this simple example the IP information is on the Wi-Fi communications
module. This IP will be used by OpenGate to send operation requests like reboot equipment or software update.
So please, setup your IP info correctly if you want to receive operations from OpenGate.

The script perform some basic caching on the device, Wi-If and relation ids for further operations
(delete, update, read). The id information is stored on disk in the following hidden (in Unix/Linux) files:
`.device_id` and `.wifi_id`. You can override the cached ids using the following configuration
parameters:

* `DEFAULT_DEVICE_ID`
* `DEFAULT_WIFI_ID`

### Read
Using `-r` option the script reads device and Wi-Fi info from OpenGate using the cached ids or the default ids from
the configuration file.

###  Update
Using `-u` option the current version is able to update device info, please change desired the data in the template
dictionary into the script.

### Delete
Using `-d` option the script deletes device and Wi-Fi info from OpenGate using the cached ids or the default ids from


## South Features

