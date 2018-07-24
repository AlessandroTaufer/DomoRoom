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
            print("add - add a chat to the allowed telegram chats list\n"
                  "remove - remove a chat from the allowed telegram chats list\n"
                  "list - list all the allowed telegram chats\n"
                  "poweroff - exit")
            choice = raw_input()
            self.digest_command(choice)

    def digest_command(self, command, source=0):  # Execute the given command
        self.logger.debug("Received command: " + str(command))
        command = command.lower().split(" ")
        if len(command) > 0:
            keyword = command.pop(0)
        else:
            self.reply_to(source, "Empty command")
            return
        if keyword == "add":
            self.reply_to(source, self.add_allowed_chat(command))
        elif keyword == "remove":
            self.reply_to(source, self.remove_allowed_chat(command))
        elif keyword == "list":
            self.reply_to(source, str(self.parent.telegram_manager.allowed_chats))
        elif keyword == "poweroff":  # TODO check if it's working properly
            self.parent.telegram_manager.broadcast_message("Bot is now offline")
            self.shut_down()
        else:
            self.reply_to(source, "Invalid input")

    def reply_to(self, target, message):  # Send a message to the given target
        if target > 0:
            self.parent.telegram_manager.send_message(target, message)
        else:
            print(message)

    def add_allowed_chat(self, command):  # Add a chat to the telegram allowed chats list
        if len(command) > 0:
            chat = command.pop(0)
        else:
            chat = raw_input("Insert the chat id: ")
        if len(chat) >= 7:
            try:
                chat = int(chat)
                self.parent.telegram_manager.add_allowed_chat(chat)
                return "Successfully added to allowed chats"
            except ValueError:
                self.logger.warning("Invalid chat id")
                return "Invalid input value"
        else:
            self.logger.warning("Invalid chat id: different digits number")
            return "Invalid input: there are not enough digits"

    def remove_allowed_chat(self, command):  # Remove a chat from the telegram allowed chats list
        if len(command) > 0:
            chat_pos = command.pop(0)
        else:
            chat_pos = raw_input("Insert the chat position/id to remove: ")
        if self.parent.telegram_manager.remove_allowed_chat(chat_pos):
            return "Successfully removed from allowed chats"
        else:
            return "Invalid value"

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