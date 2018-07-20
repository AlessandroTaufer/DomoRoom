#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


class DatabaseManager:

    def __init__(self, key):
        self.logger = logging.getLogger("DomoRoom-database_manager")  # Default logger
        self.file_names = {"telegram": "telegram.dr", "log": "log.dr"}  # Database file name
        self.key = SHA256.new(key).hexdigest()[:32]  # Encryption key
        self.filler_character = '~'  # Added at the end of the string
        self.logger.info("Successful initialized database manager")

    def init_encryptor(self, key):  # Initialize the encryptor
        self.logger.debug("Initializing encryptor")
        initialization_vector = 'This is an IV456'  # TODO Create it randomly
        encryptor = AES.new(key, AES.MODE_CBC, initialization_vector)  # File encryptor
        return encryptor

    def encrypt(self, text):  # Encode a string
        # Convert input text in a multiple of 16 in length
        next_hex = 0
        n = len(text)
        while next_hex < n:
            next_hex += 16
        for i in range(0, next_hex - n):
            text += self.filler_character

        #  Encrypt the text
        encryptor = self.init_encryptor(self.key)
        return encryptor.encrypt(text)

    def decrypt(self, encoded):  # Decrypt a string  
        encryptor = self.init_encryptor(self.key)
        txt = encryptor.decrypt(encoded)
        counter = len(encoded)-1
        while txt[counter] == self.filler_character:
            counter -= 1
        return txt[:counter+1]

    def write(self, file_name, data, encrypted=True, mode="w"):  # Write data in a file
        if file_name in self.file_names.keys():
            file_name = self.file_names[file_name]
        else:
            self.logger.warning("File name is not in the class dictionary")
        if encrypted:
            data = self.encrypt(data)

        with open(file_name, mode) as f:
            f.write(data)

    def read(self, file_name, decrypt=True):  # Get data from a file
        if file_name in self.file_names.keys():
            file_name = self.file_names[file_name]
        else:
            self.logger.warning("File name is not in the class dictionary")
        data = ""
        with open(file_name, "r") as f:
            data = f.read()
        if decrypt:
            data = self.decrypt(data)
        return data

    def write_line(self, file_name, data, line, encrypt=True):  # Write data on a specified file line
        txt = [e + "\n" for e in self.read(file_name, encrypt).split("\n")]
        if len(txt) < line + 1:
            txt += ["\n" for k in range(line - len(txt) + 1)]  # Add missing lines
            self.logger.debug("Added lines on file")
        txt[line] = data  # ("\n" if (data[-1] != "\n" and len(txt) != line + 1) else "")

        txt = "".join(txt)
        self.write(file_name, txt, encrypt)

    def read_line(self, file_name, line, decrypt=True):  # Read a specific file line
        txt = self.read(file_name, decrypt).split("\n")
        if len(txt) <= line:
            self.logger.error("Invalid line number")
            return None
        return txt[line]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    manager = DatabaseManager("database_key")


