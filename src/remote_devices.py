#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import requests
import database_manager
import time  # TODO check if import time is useless


class RemoteDevices:
    # TODO RemoteDevices needs implementation
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger("DomoRoom-RemoteDevices")
        self.devices = []
        self.load_devices()

    def __del__(self):
        # TODO warn devices that the core is shutting down
        self.backup_devices()

    def add_device(self, device):  # Add a device to the device list
        if device is not None and device not in self.devices:
            self.devices.append(device)
            return True
        self.logger.warning("Invalid device parameter as add_device method")
        return False

    def del_device(self, device):  # Remove a device from the device list
        if isinstance(device, int):
            self.devices.pop(device)
            return True
        elif device in self.devices:
            del self.devices[self.devices.index(device, 0, len(self.devices))] # TODO check if del device works
            return True
        self.logger.warning("Deleting an invalid device ")
        return False

    def get_device(self, pos):  # Return the device at the give position
        if pos >= 0 < len(self.devices):
            return self.devices[pos]

    def backup_devices(self, filename="devices"):  # Save all the devices on file
        self.logger.debug("Saving devices on file: " + filename)
        database_manager.DatabaseManager.save_object(filename, self.devices)
        self.logger.info("Devices saved on file: " + filename)

    def load_devices(self, filename="devices"):  # Load devices from a previous backup
        if database_manager.DatabaseManager.file_exist(filename):
            self.devices = self.devices + database_manager.DatabaseManager.load_object(filename)[0]
            self.logger.info("Successfully loaded devices from file: " + filename)
            return True
        else:
            self.logger.warning("Devices backup file not found")
        return False


class Device:
    # TODO Device needs implementation
    def __init__(self, name, ip_address, port):
        self.name = name
        self.ip_address = ip_address
        self.port = port

    def connect(self):  # Create a socket connection to the remote device
        pass


class EspEasyDevice(Device):  # Interface with an Esp Easy module
    def __init__(self, name,ip_address):
        Device.__init__(self, name, ip_address, None)
        self.url = "http://" + ip_address + "/control?cmd="

    def gpio_write(self, pin, status, duration=0):  # Set the remote pin at the status level
        if isinstance(pin, basestring):
            pin = self.digital_to_gpio(pin)
        status = int(status)
        command = "GPIO,"
        command += str(pin) + "," + str(status)
        if status > 1:
            command = command.replace("GPIO", "PWM")
            command += "," + str(duration)
        return self.send_command(command)

    def send_command(self, command):  # Send a command to the remote device
        try:
            r = requests.post(self.url+command)
            if r.status_code == 200:
                return True
        except:
            return False

    @staticmethod
    def digital_to_gpio(digital_pin):  # Convert a digital pin to GPIO
        # Based on https://www.letscontrolit.com/wiki/index.php/Configuration
        if isinstance(digital_pin, basestring):
            digital_pin = digital_pin.replace("D", "")
            digital_pin = int(digital_pin)
        if digital_pin == 0:
            return 16
        elif digital_pin == 3:
            return 0
        elif digital_pin == 4:
            return 2
        elif digital_pin == 5:
            return 14
        elif digital_pin == 6:
            return 12
        elif digital_pin == 7:
            return 13
        elif digital_pin == 8:
            return 15
        elif digital_pin == 11:
            return 9
        elif digital_pin == 12:
            return 10
        return digital_pin


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
    # while True:

    manager = RemoteDevices(None)
    manager.load_devices()
    # manager.add_device(dev)
    print("Devices: " + str(manager.devices))
    manager.get_device(0).gpio_write("D5", 700)
    manager.backup_devices()
