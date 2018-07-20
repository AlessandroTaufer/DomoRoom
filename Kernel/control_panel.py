#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import getpass
import database_manager
from threading import Thread


class ControlPanel:
    def __init__(self, parent=None):
        self.parent = parent  # Class parent
        self.logger = logging.getLogger("DomoRoom-telegram_manager")  # Default logger
        self.enabled = True  # Control panel status

        Thread(target=self.main_menu, args=()).start()
        print ("Enabled control panel")
        self.logger.info("Enabled control panel")

    @staticmethod
    def first_start_setup():  # Setup initial configuration
        print("\nInsert the database encryption key")
        while True:
            key = getpass.getpass("Key: ")
            key2 = getpass.getpass("Repeat Key: ")
            if key == key2:
                print("Encryption key saved\n")
                break
            else:
                print("Keys are not matching")
        print("Insert the telegram bot api token")
        token = getpass.getpass("Token: ")
        database_manager.DatabaseManager(key).write("telegram", token)

    def main_menu(self):  # User interface
        while self.enabled:
            print("\n\n\t\t\t\tCONTROL PANEL\n")
            print("a) add a chat to the allowed telegram chats list\n"
                  "b) remove a chat from the allowed telegram chats list\n"
                  "c) list all the allowed telegram chats\n"
                  "d) exit")
            choice = raw_input()
            self.digest_command(choice)

    def digest_command(self, command):  # execute the give command
        self.logger.debug("Received command: " + str(command))
        if command == 'a':
            self.add_allowed_chat()
        elif command == 'b':
            self.remove_allowed_chat()
        elif command == 'c':
            print(self.parent.telegram_manager.allowed_chats)
        elif command == 'd':  # TODO check if it's working properly
            self.shut_down()
        else:
            print ("Invalid input")

    def add_allowed_chat(self):  # Add a chat to the telegram allowed chats list
        chat = raw_input("Insert the chat id: ")
        if len(chat) >= 7:
            try:
                chat = int(chat)
                self.parent.telegram_manager.add_allowed_chat(chat)
                print("Successfully added an allowed chat")
            except ValueError:
                self.logger.warning("Invalid chat id")
                print ("Invalid input value")
        else:
            self.logger.warning("Invalid chat id: different digit number")
            print("Invalid input: there are not enough digits")

    def remove_allowed_chat(self):  # Remove a chat from the telegram allowed chats list
        chat_pos = raw_input("Insert the chat position/id to remove: ")
        if self.parent.telegram_manager.remove_allowed_chat(chat_pos):
            print("Successfully removed an allowed chat")
        else:
            print("Invalid value")

    def backup(self):  # Do a backup of all the program data
        self.parent.telegram_manager.save_data()
        self.logger.info("Backup completed")

    def shut_down(self):  # Shut down the whole program
        self.backup()
        self.enabled = False
        self.parent.telegram_manager.enabled = False
        self.logger.info("Exiting program")
        self.parent.__del__()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ControlPanel.first_start_setup()