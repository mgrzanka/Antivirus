import csv
import hashlib
import os
import chardet

from File import File

main_folder = "/home/gosia/Antivirus"


class FilesIndex:
    def __init__(self, path) -> None:
        self._path = path

    def create(self):
        fieldnames = ["path", "hash"]
        with open(self._path, 'w', newline='') as index_file:
            writer = csv.DictWriter(index_file, fieldnames=fieldnames)
            writer.writeheader()

    def remove_file(self, file_path):
        with open(self._path, 'r+') as index_file:
            reader = csv.DictReader(index_file)
            fieldnames = ["path", "hash"]
            writer = csv.DictWriter(index_file, fieldnames=fieldnames)

            rows = list(reader)
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
                try:
                    writer.writerow({"path": file.path, "hash": file.hash})
                except FileNotFoundError:
                    pass
    
    def scan(self, folder):
        try:
            if os.path.isdir(folder):
                elements = os.listdir(folder)
            else:
                return

            for element in elements:
                full_path = os.path.join(folder, element)
                if os.path.isfile(full_path):
                    file = File(full_path)
                    if not (file.is_binary() and file.is_executable()) or file.is_hidden():
                        continue
                    if file.is_malicious():
                        file.quaranteen_file()
                    else:
                        self.update_hash(file)
                else:
                    self.scan(full_path)
        except PermissionError:
            pass
    
    def quickscan(self):
        with open(self._path, 'r') as index_file:
            reader = csv.DictReader(index_file)
            for line in reader:
                file = File(line["path"])
                if file.is_malicious():
                    file.quaranteen_file()