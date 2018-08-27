#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import getpass
import database_manager
import sys
import select
from routines import RoutinesManager
from threading import Thread


class ControlPanel:
    def __init__(self, parent=None):
        self.parent = parent  # Class parent
        self.logger = logging.getLogger("DomoRoom-telegram_manager")  # Default logger
        self.enabled = True  # Control panel status
        self.keywords = self.parent.database_manager.load_keywords()  # List of all the commands keywords
        Thread(target=self.main_menu, args=()).start()
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
        token = getpass.getpass("Token: ")  # TODO check if the token is working
        database_manager.DatabaseManager(key).write("telegram", token)

    @staticmethod
    def console_input(timeout=20):  # Get an input from the console
        i, o, e = select.select([sys.stdin], [], [], timeout)

        if i:
            return sys.stdin.readline().strip()
        else:
            return None

    def main_menu(self):  # User interface
        choice = ""
        while self.enabled:
            if choice is not None:
                if choice != "":
                    self.digest_command(choice)
                print("\n\n\t\t\t\tCONTROL PANEL\n")
                print(self.get_help())
            choice = self.console_input(5)

    def digest_command(self, command, source=0):  # Execute the given command
        self.logger.debug("Received command: " + str(command))
        command = command.lower().split(" ")
        if len(command) > 0:
            keyword = command.pop(0)
        else:
            self.reply_to(source, "Empty command")
            return
        # TODO add ping command
        if keyword == "addme" and source not in self.parent.telegram_manager.allowed_chats:  # TODO debug addme
            warning_txt = "Chat '" + str(source) + "' requested to be enabled to use the bot"
            self.broadcast_message(warning_txt)
            self.reply_to(source, "Your request has been submitted")
        elif keyword == self.keywords.get("help").get("name"):
            help = "HELP:\n" + self.get_help()
            self.reply_to(source, help)
        elif keyword == self.keywords.get("add_chat").get("name"):
            self.reply_to(source, self.add_allowed_chat(command))
        elif keyword == self.keywords.get("remove_chat").get("name"):
            self.reply_to(source, self.remove_allowed_chat(command))
        elif keyword == self.keywords.get("list_chats").get("name"):
            self.reply_to(source, str(self.parent.telegram_manager.allowed_chats))
        elif keyword == self.keywords.get("telegram_reminder").get("name"):
            self.reply_to(source, self.set_telegram_reminder(command))
        elif keyword == self.keywords.get("list_routines").get("name"):
            self.reply_to(source, str(self.parent.routines.routines_to_string()))
        elif keyword == self.keywords.get("capture_image").get("name"):
            self.reply_to(source, self.capture_image(command))
        elif keyword == self.keywords.get("security_system").get("name"):
            self.reply_to(source, self.security_system(command))
        elif keyword == self.keywords.get("power_off").get("name"):
            self.parent.telegram_manager.broadcast_message("Bot is now offline")
            self.shut_down()
        else:
            self.reply_to(source, "Invalid input")

    def broadcast_message(self, text):  # Broadcast a message on console, telegram chats and logger
        self.parent.telegram_manager.broadcast_message(text)
        self.logger.info(text)
        print(text)

    def reply_to(self, target, message):  # Send a message to the given target
        if target > 0:
            self.parent.telegram_manager.send_message(target, message)
        else:
            print(message)

    def add_allowed_chat(self, command):  # Add a chat to the telegram allowed chats list
        if len(command) > 0:
            chat = command.pop(0)
        else:
            print("Insert the chat id: ")
            chat = self.console_input()
        if chat is not None and len(chat) >= 7:
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
            print("Insert the chat position/id to remove: ")
            chat_pos = self.console_input()
        if self.parent.telegram_manager.remove_allowed_chat(chat_pos):
            return "Successfully removed from allowed chats"
        else:
            return "Invalid value"

    def set_telegram_reminder(self, command):  # Set a telegram reminder
        if len(command) >= 4:
            name = command.pop(0)
            date = command.pop(0)
            time = command.pop(0)
            chat = command.pop(0)
            message = " ".join(command)
        else:
            print("Insert the routine name")
            name = self.console_input()
            print("Insert the date: (format dd/mm/yy)")
            date = self.console_input()
            print("Insert the time: (format hh:mm:ss)")
            time = self.console_input()
            print ("Insert the message: ")
            message = self.console_input()
            print("Insert the address chat:  (return to broadcast)")
            chat = self.console_input()
            if chat == "":
                chat = -1
        try:
            chat = int(chat)
            date_time = self.datetime_format(date, time)
            self.parent.routines.attach_telegram_alert_routine(name, message, chat, date_time)
            self.logger.info("Reminder " + name + " set")
            return "Successfully set the telegram reminder"
        except:
            self.logger.warning("An error has occurred while setting a reminder")
        return "Invalid value"

    @staticmethod
    def datetime_format(date, time):  # Return a date time object from a date string
        date = [int(d) for d in date.split("/")]
        date.reverse()
        if date[0] < 2000:
            date[0] = 2000 + date[0]
        if time is None or time is "":
            time = []
        else:
            time = [int(d) for d in time.split(":")]
        while len(time) < 4:
            time.append(0)
        param = date + time
        return RoutinesManager.convert_to_datetime(*param)

    def capture_image(self, command):  # Capture an image an send it to the corresponding chat
        # TODO save a local copy in imgs folder
        if len(command) > 0:
            chat_pos = command.pop(0)
        else:
            self.parent.telegram_manager.broadcast_image(self.parent.camera_manager.last_shot)
            return "Successfully broadcasted picture"
        if self.parent.telegram_manager.send_image(chat_pos, self.parent.camera_manager.last_shot):
            return "Successfully sent picture"
        else:
            return "Invalid value"

    def security_system(self, command):  # Enable / Disable the security system
        if len(command) > 0:
            status = command.pop(0)
        else:
            print("Turn on/OFF: ")
            status = self.console_input()
        status = status.lower() == "on"
        if status:
            self.parent.camera_manager.turn_on_motion_detection()
            return "Security system enabled"
        else:
            self.parent.camera_manager.turn_off_motion_detection()
            return "Security system disabled"

    def backup(self):  # Do a backup of all the program data
        self.parent.telegram_manager.save_data()
        self.logger.info("Backup completed")

    def get_help(self):  # Returns a string containing all the commands
        return "\n".join([e.get("name") + " - " + e.get("description") for e in self.keywords.values()])

    def shut_down(self):  # Shut down the whole program
        self.backup()
        self.enabled = False
        self.parent.telegram_manager.enabled = False
        self.parent.routines.enabled = False
        self.parent.camera_manager.enabled = False
        self.parent.camera_manager.turn_off_motion_detection()
        self.logger.info("Exiting program")
        self.parent.__del__()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ControlPanel.first_start_setup()
