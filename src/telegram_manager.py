#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import telegram
import time
from cv2 import imwrite
from telegram.error import NetworkError, Unauthorized
from threading import Thread


class TelegramManager:

    def __init__(self, parent):
        self.parent = parent  # Class parent
        self.allowed_chats = []  # Chats allowed to use the bot
        self.bot = None  # Telegram bot instance
        self.update_id = None  # Id of the different updates
        self.logger = logging.getLogger("DomoRoom-telegram_manager")  # Default logger
        self.bot_tag = None  # Tag of the current bot
        self.enabled = True  # update listener status

        self.load_data()
        self.attach_listener()
        self.logger.error("Debug logger")

    def load_data(self):  # Loads data from a file
        self.logger.debug("Telegram Manager loading data from file")
        if self.parent.database_manager is None:
            self.logger.error("Could not load data, database manager is None")
        self.bot_tag = self.parent.database_manager.read_line("telegram", 0)
        chats = self.parent.database_manager.read_line("telegram", 1)
        if chats is not None:
            chats = chats.split(",")
            self.allowed_chats = [int(chat) for chat in chats]
        self.logger.debug("Allowed chats " + str(self.allowed_chats))
        pass

    def attach_listener(self):  # Initialize and attach a telegram updates listener
        self.bot = telegram.Bot(self.bot_tag)
        self.logger.debug(self.bot)
        self.broadcast_message("Bot is now online")
        if self.bot is None:
            self.logger.error("Failed to initialize telegram bot " + str(self.__class__))
            exit(1)
        try:
            self.update_id = self.bot.get_updates()[0].update_id + 1
        except IndexError:
            self.update_id = None
            self.logger.warning("Update index error " + str(self.__class__))
        Thread(target=self.updates_listener, args=()).start()

    def updates_listener(self):  # Listen from telegram updates
        while self.enabled:
            try:
                for update in self.bot.get_updates(offset=self.update_id, timeout=10):
                    self.update_id = update.update_id + 1
                    if update.message:
                        self.on_message(update)

            except NetworkError:  # An network error has occurred
                time.sleep(1)
                self.logger.warning("Network error ")
            except Unauthorized:  # The user has removed or blocked the bot.
                self.update_id += 1

    def on_message(self, update, extra_function=None):  # Verify and elaborate the received message
        received_text = update.message.text
        current_chat_id = update.message.chat_id
        self.logger.debug("message chat id " + str(current_chat_id))
        if current_chat_id in self.allowed_chats:
            self.logger.info("Received message:" + received_text)
            self.parent.control_panel.digest_command(received_text, current_chat_id)
        else:
            if received_text == "addme":
                self.parent.control_panel.digest_command(received_text, current_chat_id)
            update.message.reply_text("This bot is classified, 'addme' to request the clearance")
            self.logger.warning("Received unauthorized message from: " + str(self.bot.get_chat(update.message.chat_id)))
            self.logger.warning("unauthorized message content: " + str(received_text))
        try:
            extra_function(update.message)
        except TypeError:
            self.logger.debug("extra function is None ")

    def send_message(self, chat_id, text):  # Send a message to the given chat
        try:
            self.bot.sendMessage(chat_id, text)
        except:
            self.logger.warning("Failed to send message to the current chat " + str(chat_id))

    def send_image(self, chat_id, image):  # Send an image to the given chat
        try:
            path = "../tmp/tmp.jpg"
            if not isinstance(image, basestring):
                imwrite(path, image)
            else:
                path = image
            image = open(path, "rb")
            self.bot.send_photo(chat_id, image)
            return True
        except:
            self.logger.warning("Failed to send photo to the current chat " + str(chat_id))
        return False

    def broadcast_message(self, text):  # Broadcast a message to all the allowed chats
        for chat in self.allowed_chats:
            self.send_message(chat, text)
        return True

    def broadcast_image(self, image):  # Broadcast a message to all the allowed chats
        for chat in self.allowed_chats:
            self.send_image(chat, image)
        return True

    def add_allowed_chat(self, chat_id):  # Add a chat to the telegram allowed chats list
        self.logger.info("Adding chat: " + str(chat_id))
        self.allowed_chats.append(chat_id)
        self.send_message(chat_id, "You have been added to the allowed chats")
        self.logger.debug("Current allowed chats: " + str(self.allowed_chats))

    def remove_allowed_chat(self, pos):  # Remove a chat from the telegram allowed chats list
        try:
            pos = int(pos)
            if 0 <= pos < len(self.allowed_chats):
                tmp_chat = self.allowed_chats.pop(pos)
                self.logger.info("Removed chat: " + str(tmp_chat))
                return True
            elif len(str(pos)) == 8:
                self.allowed_chats.remove(pos)
                return True
        except (ValueError, IndexError, TypeError):
            logging.warning("Failed to remove chat: invalid parameter " + str(pos))
        return False

    def save_data(self):  # Save the data on file  # TODO save telegram data by pickle
        chats = ""
        for c in self.allowed_chats:
            chats += str(c) + ","
        chats = chats[:-1]
        self.parent.database_manager.write_line("telegram", chats, 1)
        self.logger.info("Saving telegram data")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    t = TelegramManager(None)
