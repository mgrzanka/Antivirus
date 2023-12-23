import csv
import hashlib
import os

main_folder = "/home/gosia/Antivirus"


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


class FilesIndex:
    def __init__(self, path) -> None:
        self._path = path

    def create(self):
        fieldnames = ["path", "hash"]
        with open(self._path, 'w', newline='') as index_file:
            writer = csv.DictWriter(index_file, fieldnames=fieldnames)
            writer.writeheader()


    def update_hash(self, file: File):
        with open(self._path, 'r+') as index_file:
            reader = csv.DictReader(index_file)
            fieldnames = ["path", "hash"]
            writer = csv.DictWriter(index_file, fieldnames=fieldnames)

            updated = False
            rows = list(reader)
            for row in rows:
                if row["path"] == file.path:
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
    
    def exclude_hidden(self, file_path, elements):
        path, element = os.path.split(file_path)
        if path and element:
            elements.append(element)
            self.exclude_hidden(path, elements)
        else:
            elements.append(element)

        for element in elements:
            if element.startswith('.'):
                elements = None
        return elements

    def scan(self, folder):
        try:
            if os.path.isdir(folder):
                elements = os.listdir(folder)
            else:
                return

            for element in elements:
                full_path = os.path.join(folder, element)
                if not self.exclude_hidden(full_path, []):
                    continue
                if os.path.isfile(full_path):
                    file = File(full_path)
                    self.update_hash(file)
                else:
                    self.scan(full_path)
        except PermissionError:
            pass