#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging


class RemoteDevices:
    # TODO RemoteDevices needs implementation
    def __init__(self):
        self.logger = logging.getLogger("DomoRoom-RemoteDevices")
        self.devices = []

    def add_device(self, device):  # Add a device to the device list
        if device is not None and device not in self.devices:
            self.devices.append(device)
            return True
        self.logger.warning("Invalid device parameter as add_device method")
        return False

    def del_device(self, device):  # Remove a device from the device list
        if device in self.devices:
            del self.devices[self.devices.index(device,0,len(self.devices))]
            return True
        self.logger.warning("Deleting an invalid device ")
        return False

    def get_device(self, pos):  # Return the device at the give position
        if pos >= 0 < len(self.devices):
            return self.devices[pos]


class Device:
    # TODO Device needs implementation
    def __init__(self, ip_address, port, script):
        self.ip_address = ip_address
        self.port = port
        self.scripts = script

    def connect(self):  # Create a socket connection to the remote device
        pass


class Sensor(Device):
    # TODO Sensor needs implementation
    '''
       Every device has some scripts to control itself. They are contained in a dictionary.
       Keywords that every device must have:
       setup, read
    '''
    def __init__(self, ip_address, script):
        Device.__init__(ip_address, script)
        self.scripts["setup"]()

    def get_value(self):  # Get the sensor value
        return self.scripts["read"]()

