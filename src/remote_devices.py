#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import requests
import time # TODO check if import time is useless


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
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    def connect(self):  # Create a socket connection to the remote device
        pass


class EspEasyDevice(Device):  # Interface with an Esp Easy module
    def __init__(self, ip_address):
        Device.__init__(self, ip_address, None)
        self.url = "http://" + ip_address + "/control?cmd=event,"

    # TODO check if send_signal is working
    def send_signal(self, pin, status):  # Set the remote pin at the status level
        status = int(status)
        command = "A" + str(pin) + str(status)
        try:
            r = requests.post(self.url+command)
            if r.status_code == 200:
                return True
        except:
            pass
        return False


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


if __name__ == "__main__":
    while True:
        EspEasyDevice("192.168.1.200").send_signal(1, False)
        time.sleep(0.3)
        EspEasyDevice("192.168.1.200").send_signal(1, True)
        time.sleep(0.3)
