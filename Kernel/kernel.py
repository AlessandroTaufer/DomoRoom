#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import TelegramManager.telegram_manager


class Kernel:
    def __init__(self):
        self.init_logging()
        self.telegram_manager = TelegramManager.telegram_manager.TelegramManager(self)
        self.database_manager = None
        self.remote_devices = None
        self.data_mining = None
        self.integrity_system = None
        self.routines = None
        self.remote_controller = None

    @staticmethod
    def init_logging():  # Initialize console logging
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return


if __name__ == "__main__":
    Kernel()
