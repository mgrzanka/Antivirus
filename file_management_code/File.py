import os
import shutil
import hashlib
import chardet
import sqlite3

from messages_code.Messages import SuccessMessage, FailureMessage


class File:
    '''
    A class used to represent single file

    Attributes
    -------------
    path: str
        total path to the file
    main_folder: str
        total path to main folder of the program

    Properties
    ---------------
    path: str
        total path to the file
    hash: str
        MD5 hash of the file

    Methods
    --------------
    is_binary(): returns bool
        checks if file is binary
    is_executable(): returns bool
        checks if the file has execute permission
    is_hidden(): returns bool
        checks if file is a hidden file
    is_malicious(): returns bool
        checks if virus hash matches hash from database
    quarantine_file(): returns nothing
        moves malicious file to .quarantine folder and take away it's permissions

    External libraries: chardet
    '''
    def __init__(self, path: str, main_folder) -> None:
        '''
        path: str
            total path to the file
        main_folder: str
            total path to main folder of the program
        '''
        self._path = path
        self._main_folder = main_folder

    @property
    def path(self):
        '''total path to the file
        str
        '''
        return self._path

    @property
    def hash(self):
        '''MD5 hash of the file
        str
        '''
        hashMD5 = hashlib.md5()
        try:
            with open(self.path, 'rb') as file:
                file_content = file.read()
                hashMD5.update(file_content)
            return hashMD5.hexdigest()
        except Exception:
            pass

    def is_binary(self):
        ''' checks if the file is binary
        If file content has 0x00, it's text file
        If file content has '#!', it's binary file

        In other cases, program uses chardet.UniversalDetector class to detect
        text coding of the file. If it can't recognise any known coding,
        program considers this file binary

        Return True if file is binary, False if it's a text

        Parameters
        -------------
        None
        '''
        real_path = os.path.realpath(self.path)
        try:
            with open(real_path, 'rb') as file:
                if b'\x00' in file.read(1024):
                    return False
                file.seek(0)
                if b'#!' in file.read(1024):
                    return True
                file.seek(0)
                detector = chardet.UniversalDetector()
                for line in file.readlines():
                    detector.feed(line)
                    if detector.done:
                        break
                detector.close()
                result = detector.result
                return result["confidence"] < 0.8
        except PermissionError:
            pass

    def is_executable(self):
        '''checks if the file has execute permission

        Returns True if the file has x in properties,
                False if it doesn't

        Parameters
        ------------
        None

        '''
        return os.access(self.path, os.X_OK)

    def is_hidden(self):
        '''checks if file is a hidden file
        Function split whole path to the list and then checks if any of the
        list elements has '.' at the begining

        Returns True if the file has a hidden component in it's path,
                False if it's completly shown

        Parameters
        --------------
        None
        '''
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
        '''checks if virus hash matches hash from database
        Function uses external database through sqlite3 module
        It takes hash of the file and looks if there is a matching hash in this database

        Returns True if there is a matching hash,
                False is it's not

        Parameters
        -------------
        None
        '''
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
        '''moves malicious file to .quarantine folder and take away it's permissions
        Function tries to move malicious file to folder .quarantine and it sets
        it's permissions to 0o000 (None permissions at all)

        If it succeed to do so, it displays message informing user
        about the virus and it's new location and lack of permissions
        If it fails, it displays message informing user about failure and virus' location

        Returns nothing

        Parameters
        -----------
        None
        '''
        new_file_path = None
        try:
            destination_path = os.path.join(self._main_folder, ".quarantine")
            file_path = self.path
            shutil.move(file_path, destination_path)
            new_file_path = os.path.join(destination_path, os.path.split(file_path)[1])
            os.chmod(new_file_path, 0o000)
            message = SuccessMessage(new_file_path, self.path)
            message.display_message()
        except Exception:
            failure_message = FailureMessage(new_file_path, file_path)
            failure_message.display_message()
