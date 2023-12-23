import os
import hashlib
import chardet
import sqlite3


class File:
    def __init__(self, path: str) -> None:
        self._path = path
    
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
        with open(self.path, 'rb') as file:
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
        db_path = "/home/gosia/Antivirus/HashDB"
        database = sqlite3.connect(db_path)
        database_curor = database.cursor()
        result = database_curor.execute("SELECT * FROM HashDB WHERE hash=?", (self.hash,))
        result = result.fetchall()
        if result:
            return True
        else:
            return False

    def quaranteen_file(self):
        # Informacja o zamknieciu pliku w kwarantannie przesyłana na maila
        pass