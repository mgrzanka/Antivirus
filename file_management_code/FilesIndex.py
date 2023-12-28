import csv
import os
import time
from multiprocessing import Process

from .File import File
from messages_code.Messages import PermissionErrorMessage


class FilesIndex:
    def __init__(self, path, main_folder) -> None:
        self._path = path
        self._main_folder = main_folder
        self._error_occured = False

    def handle_permission_error(self):
        self._error_occured = True
        message = PermissionErrorMessage()
        message.display_message()
    
    def should_exit(self):
        return self._error_occured
    
    def create(self):
        try:
            fieldnames = ["path", "hash"]
            with open(self._path, 'w', newline='') as index_file:
                writer = csv.DictWriter(index_file, fieldnames=fieldnames)
                writer.writeheader()
        except PermissionError:
            self.handle_permission_error()

    def remove_file(self, file_path):
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

    def update_hash(self, file: File):
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

    def scan(self, folder):
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

    def scan_process(self, folder):
        proces = Process(target=self.scan, args=(folder,))
        proces.start()
        return proces

    def quickscan(self):
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
