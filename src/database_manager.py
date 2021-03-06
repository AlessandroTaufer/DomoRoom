#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import os.path
import pickle
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from collections import OrderedDict


class DatabaseManager:
    file_names = {"telegram": "telegram.dr", "log": "log.dr", "keywords": "keywords.txt",
                  "devices": "devices.dr"}  # Database file name
    file_path = "../resources/files/"  # Files path

    def __init__(self, key):
        self.logger = logging.getLogger("DomoRoom-database_manager")  # Default logger
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
        file_name = DatabaseManager.generate_filename(file_name)
        if encrypted:
            data = self.encrypt(data)

        with open(file_name, mode) as f:
            f.write(data)

    def read(self, file_name, decrypt=True):  # Get data from a file
        file_name = DatabaseManager.generate_filename(file_name)
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
        single_line = False
        if not isinstance(line, list):
            line = [line]
            single_line = True
        txt = self.read(file_name, decrypt).split("\n")
        if len(txt) <= max(line):
            self.logger.error("Invalid line number")
            return None
        if single_line:
            return txt[line[0]]
        return [txt[pos] for pos in line]

    def load_keywords(self):  # Loads the keywords set from a file
        keywords = self.read("keywords", False).split("\n")
        dictionary = OrderedDict()
        for line in keywords:
            tmp_list = line.split(",")
            for i in range(len(tmp_list)):
                if tmp_list[i][0] == " ":
                    tmp_list[i] = tmp_list[i][1:]
            try:
                dictionary[tmp_list[0]] = {"name": tmp_list[1], "description": tmp_list[2]}
            except IndexError:
                self.logger.error("Invalid keywords file line")
        self.logger.info("Successfully loaded keywords from file")
        return dictionary

    @staticmethod
    def generate_filename(file_name):  # Autocomplete the filename if it's in the file_names list
        if file_name in DatabaseManager.file_names.keys():
            file_name = DatabaseManager.file_path + DatabaseManager.file_names[file_name]
        else:
            logging.warning("File name is not in the class dictionary")
        return file_name

    # TODO encrypt pickle objects
    # TODO debug pickle methods
    @staticmethod
    def save_object(file_name, obj):  # Save the given objects on file (overwrites the file)
        file_name = DatabaseManager.generate_filename(file_name)
        with open(file_name, 'wb') as output:
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_object(file_name):  # Load all the objects from a file
        file_name = DatabaseManager.generate_filename(file_name)
        with open(file_name, 'rb') as input:
            objs = []
            while True:
                try:
                    objs.append(pickle.load(input))
                except EOFError:
                    break
        return objs

    @staticmethod
    def file_exist(file_name):  # Return true if the given file exists
        file_name = DatabaseManager.generate_filename(file_name)
        return os.path.isfile(file_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    manager = DatabaseManager("key").file_exist("telegram")
