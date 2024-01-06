import csv
import os
from multiprocessing import Process

from .File import File
from messages_code.Messages import PermissionErrorMessage


class FilesIndex:
    '''
    A class representing single index file

    Attributes
    -------------
    path: str
        total path to the file index
    main_folder: str
        total path to the main folder of the program (Antivirus folder)
    error_occured: bool
        flag to potencial error caused by no permission to create index file

    Properties
    --------------
    should_exit(): bool
        returns error_occured flag

    Methods
    -------------
    handle_parmission_error(): returns nothing
        displays permission error message if error occured
    create(): returns nothing
        creates new index file with headers "path" and "hash"
    remove_file(file_path: str): returns nothing
        removes file from index
    update_hash(file: File): returns nothing
        adds file to index if it's not there, updates it's hash otherwise
    scan(folder: path): returns nothing
        adds all binary, executable, not-hidden and not-malicious files to index
        if malicious, quarantine it
    scan_process(folder: path): returns Process class instance
        starts process of scan() function for given folder
    quickscan(): returns nothing
        updates potential non-validity of files index
    '''
    def __init__(self, path, main_folder: str) -> None:
        '''
        path: str
            total path to the file index
        main_folder: str
            total path to the main folder of the program (Antivirus folder)
        error_occured: bool
            flag to potencial error caused by no permission to create index file
        '''
        self._path = path
        self._main_folder = main_folder
        self._error_occured = False

    @property
    def should_exit(self) -> bool:
        '''error_occured flag
        bool
        '''
        return self._error_occured

    def handle_permission_error(self) -> None:
        '''displays permission error message if error occured
        Function sets error_occured flag to True and displays message that there is
        no sudo permisions

        Returns nothing

        Parameters
        --------------
        None
        '''
        self._error_occured = True
        message = PermissionErrorMessage()
        message.display_message()

    def create(self) -> None:
        '''creates new index file with headers "path" and "hash"
        Function tries do create index file with headers, if there is no permission to do so,
        calls function hendle_permision_error()
        If there is .index.csv file alread, delete it and create new to be sure no sudo protection
        will work

        Returns nothing

        Parameters
        --------------
        None
        '''
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
            fieldnames = ["path", "hash"]
            with open(self._path, 'w', newline='') as index_file:
                writer = csv.DictWriter(index_file, fieldnames=fieldnames)
                writer.writeheader()
        except PermissionError:
            self.handle_permission_error()

    def remove_file(self, file_path: str) -> None:
        '''removes file from index
        Function creates a list of rows in index. If path of any of the rows matches
        given file path, it removes this file from the list and rewrites index

        Returns nothing

        Parameters
        ------------
        file_path: str
            total path of file that should be deleted from index
        '''
        with open(self._path, 'r') as index_file:
            reader = csv.DictReader(index_file)
            fieldnames = ["path", "hash"]
            rows = list(reader)
        with open(self._path, 'w') as index_file:
            writer = csv.DictWriter(index_file, fieldnames=fieldnames)

            for row in rows:
                if row["path"] == file_path:
                    rows.remove(row)
                    break

            index_file.seek(0)
            writer.writeheader()
            writer.writerows(rows)

    def update_hash(self, file: File) -> None:
        '''adds file to index if it's not there, updates it's hash otherwise
        Function creates a list of rows in index and iterates through it
        If it finds file in the list that has same path as the given file:
        - if the hash is the same, do nothing
        - if the hash doesn't match, update it
        If it doesn't find file in the list that has same path as the given file,
        add this file to the index

        Returns nothing

        Parameters
        -------------
        file: File
            represents file to update in index
        '''
        with open(self._path, 'r+') as index_file:
            reader = csv.DictReader(index_file)
            fieldnames = ["path", "hash"]
            writer = csv.DictWriter(index_file, fieldnames=fieldnames)

            updated = False
            rows = list(reader)
            for row in rows:
                if row["path"] == file.path and row["hash"] == file.hash:
                    return
                elif row["path"] == file.path and row["hash"] != file.hash:
                    row["hash"] = file.hash
                    updated = True
                    break

            if updated:
                index_file.seek(0)
                writer.writeheader()
                writer.writerows(rows)
            else:
                writer.writerow({"path": file.path, "hash": file.hash})

    def scan(self, folder: str) -> None:
        '''adds all binary, executable, not-hidden and not-malicious files to index
        Function go recursively through all of the directories and files in given folder.
        If the file is binary, executable and not hidden, checks if it's malicious.
        If it is malicious, call file.quarantine() function, if not, call update_hash() function

        Returns nothing

        Parameters
        ------------
        folder: str
            total path to folder being scaned
        '''
        if os.path.isdir(folder):
            elements = os.listdir(folder)
        else:
            return

        for element in elements:
            full_path = os.path.join(folder, element)
            if os.path.isfile(full_path):
                file = File(full_path, self._main_folder)
                if not (file.is_binary() and file.is_executable()) or file.is_hidden():
                    continue
                if file.is_malicious():
                    file.quarantine_file()
                else:
                    self.update_hash(file)
            else:
                self.scan(full_path)

    def scan_process(self, folder: str) -> Process:
        '''starts process of scan() function for given folder
        Function creates multiprocessing.Proces object representing scan for one of the main
        folders given in json settings file and starts it

        Returns proces object, so it can be stored in list in the main program for join()

        Parameters
        --------------
        folder: str
            directory for which the scan should be started
        '''
        proces = Process(target=self.scan, args=(folder,))
        proces.start()
        return proces

    def quickscan(self) -> None:
        '''updates potential non-validity of files index
        Function goes through every file in index and checkes if it's malicious.
        If it is, it calls file.quarantine() function and removes it from the index
        If it's not, it updates it's hash in case it was modified and program missed it

        Returns nothing

        Parameters
        -------------
        None
        '''
        with open(self._path, 'r') as index_file:
            reader = csv.DictReader(index_file)
            for line in reader:
                file = File(line["path"], self._main_folder)
                if file.is_malicious():
                    file.quarantine_file()
                    self.remove_file(file.path)
                else:
                    self.update_hash(file)
            print("Quick scan completed")
