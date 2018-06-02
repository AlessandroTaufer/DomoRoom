#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import telegram
import time
from telegram.error import NetworkError, Unauthorized
from threading import Thread


class TelegramManager:

    def __init__(self, parent):
        self.parent = parent  # Class parent
        self.allowed_chats = [116360988]  # Chats allowed to use the bot
        self.bot = None  # Telegram bot instance
        self.update_id = None  # Id of the different updates
        self.logger = logging.getLogger("telegram_manager")
        # TODO Load the bot tag and the allowed chats from the database
        self.bot_tag = "560682687:AAGHYh7rLv43Og-Mvyejo-qNeJIP_zHs4FY"  # Tag of the current bot

        # self.load_data()
        self.attach_listener()

    def load_data(self):  # Loads data from a file
        self.logger.debug("Telegram Manager loading data from file")
        self.parent.database_manager.load()
        pass    # TODO implement method

    def attach_listener(self):  # Initialize and attach a telegram updates listener
        self.bot = telegram.Bot(self.bot_tag)
        self.logger.debug(self.bot)
        self.broadcast_message("Bot is now online")
        if self.bot is None:
            self.logger.error("Failed to initialize telegram bot " + str(self.__class__))
            exit(1)
        try:
            self.update_id = self.bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None
            self.logger.warning("Update index error " + str(self.__class__))
        Thread(target=self.updates_listener, args=()).start()

    def updates_listener(self):  # Listen from telegram updates
        while True:
            try:
                for update in self.bot.get_updates(offset=self.update_id, timeout=10):
                    self.update_id = update.update_id + 1

                    if update.message:  # your bot can receive updates without messages
                        self.on_message(update)

            except NetworkError:  # An network error has occurred
                time.sleep(1)
                self.logger.warning("Network error " + str(self.__class__))
            except Unauthorized:  # The user has removed or blocked the bot.
                self.update_id += 1
                self.logger.warning("Unauthorized access " + str(self.__class__))

    def on_message(self, update, extra_function=None):  # Verify and elaborate the received message
        received_text = update.message.text
        current_chat_id = update.message.chat_id
        if current_chat_id in self.allowed_chats:
            self.logger.info("Received message:" + received_text)
            update.message.reply_text(received_text)
        else:
            update.message.reply_text("You are not allowed to use this bot")
            self.logger.warning("Received unauthorized message from: " + str(self.bot.get_chat(update.message.chat_id)))
            self.logger.warning("unauthorized message content: " + received_text)
        try:
            extra_function(update.message)
        except TypeError:
            self.logger.debug("extra function is None in " + str(self.__class__))

    def send_message(self, chat_id, text):  # Send a message to the given chat
        try:
            self.bot.sendMessage(chat_id, text)
        except:
            self.logger.warning("Failed to send message to the current chat " + str(chat_id))

    def broadcast_message(self, text):  # Broadcast a message to all the allowed chats
        for chat in self.allowed_chats:
            self.send_message(chat, text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    TelegramManager(None)
