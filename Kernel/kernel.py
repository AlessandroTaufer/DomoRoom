#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import TelegramManager.telegram_manager
import database_manager
import control_panel
# TODO method to init the domoRoom at the first access
# TODO manage random errors (404)


class Kernel:
    def __init__(self):
        self.init_logging('logfile')
        key = raw_input("Insert the key: ")  # TODO verify & hide the key
        self.database_manager = database_manager.DatabaseManager(key)
        self.telegram_manager = TelegramManager.telegram_manager.TelegramManager(self)
        self.control_panel = control_panel.ControlPanel(self)
        self.remote_devices = None
        self.data_mining = None
        self.integrity_system = None
        self.routines = None
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
    Kernel()
