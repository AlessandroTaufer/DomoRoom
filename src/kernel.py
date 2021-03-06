#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import telegram_manager
import database_manager
import control_panel
import routines
import camera_manager
import remote_devices


# TODO manage random errors (404)
# TODO manage .dr and pyc


class Kernel:
    def __init__(self, verbose):
        logfile = "../resources/files/logfile"
        if verbose:
            logfile = ""
        self.init_logging(logfile)
        self.logger = logging.getLogger("DomoRoom-kernel")  # Default logger
        if not database_manager.DatabaseManager.file_exist("telegram"):
            self.logger.warning("Resources not found, initializing 'first access setup'")
            control_panel.ControlPanel.first_access_setup()

        key = raw_input("Insert the key: ")  # TODO verify & hide the key
        self.database_manager = database_manager.DatabaseManager(key)
        self.camera_manager = camera_manager.CameraManager(self)
        self.telegram_manager = telegram_manager.TelegramManager(self)
        self.control_panel = control_panel.ControlPanel(self)
        self.remote_devices = remote_devices.RemoteDevices(self)
        self.data_mining = None
        self.integrity_system = None
        self.routines = routines.RoutinesManager(self)
        self.remote_controller = None

    def __del__(self):
        logging.info("Shutting down kernel")

    @staticmethod
    def init_logging(file_name=""):  # Initialize console logging
        if file_name != "":
            file_name += ".log"
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=log_format, filename=file_name, filemode='w')
        return


if __name__ == "__main__":
    Kernel(verbose=False)
