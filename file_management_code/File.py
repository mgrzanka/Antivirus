import os
import shutil
import hashlib
import chardet
import sqlite3

from messages_code.Messages import SuccessMessage, FailureMessage

class File:
    def __init__(self, path: str, main_folder) -> None:
        self._path = path
        self._main_folder = main_folder
    
    @property
    def path(self):
        return self._path

    @property
    def hash(self):
        hashMD5 = hashlib.md5()
        try:
            with open(self.path, 'rb') as file:
                file_content = file.read()
                hashMD5.update(file_content)
            return hashMD5.hexdigest()
        except FileNotFoundError:
            pass
       
    def is_binary(self):
        real_path = os.path.realpath(self.path)
        with open(real_path, 'rb') as file:
            if b'\x00' in file.read(1024):
                return False
            if b'#!' in file.read(1024):
                return True
            detector = chardet.UniversalDetector()
            for line in file.readlines():
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
            result = detector.result
            return result["confidence"] < 0.9
    
    def is_executable(self):
        return os.access(self.path, os.X_OK)
    
    def is_hidden(self):
        path = self.path
        elements = []
        while True:
            path, element = os.path.split(path)
            if element:
                elements.insert(0, element)
            else:
                if path:
                    elements.insert(0, path)
                break
        for element in elements:
            if element.startswith("."):
                return True
        return False

    def is_malicious(self):
        db_path = os.path.join(self._main_folder, ".important_files/HashDB")
        database = sqlite3.connect(db_path)
        database_curor = database.cursor()
        result = database_curor.execute("SELECT * FROM HashDB WHERE hash=?", (self.hash,))
        result = result.fetchall()
        if result:
            return True
        else:
            return False

    def quarantine_file(self):
        try:
            destination_path = os.path.join(self._main_folder, ".quarantine")
            file_path = self.path
            shutil.move(file_path, destination_path)
            new_file_path = os.path.join(destination_path, os.path.split(file_path)[1])
            os.chmod(new_file_path, 0o000)
            success_message = SuccessMessage(new_file_path)
            success_message.display_message()
        except Exception:
            failure_message = FailureMessage(file_path, new_file_path)
            failure_message.display_message()
