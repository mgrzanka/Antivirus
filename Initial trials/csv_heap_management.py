import hashlib
import csv
import os


def hash_MD5(file_path: str) -> str:    # returns hash of the file
    hash = hashlib.md5()
    with open(file_path, 'rb') as file:
        file_content = file.read()
        hash.update(file_content)
        return hash.hexdigest()


def if_empty():
    with open("scan_heap", "r", newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        return not any([row for row in csv_reader if row])


def csv_add_path(path: str, new_file=False):    # adds a record to the csv file
    if new_file:
        with open("scan_heap", "w", newline='') as csv_file:
            fieldnames = ["path", "hash"]
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
    else:
        with open("scan_heap", "a", newline='') as csv_file:
            hash = hash_MD5(path)
            fieldnames = ["path", "hash"]
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writerow({"path": path, "hash": hash})


def csv_delete_path():
    with open("scan_heap", "r") as heap_read:
        csv_reader = csv.DictReader(heap_read)
        new_heap = list(csv_reader)[1:]
    with open("scan_heap", "w", newline='') as heap_write:
        fieldnames = ["path", "hash"]
        csv_writer = csv.DictWriter(heap_write, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(new_heap)


# FULL SCANNING
def FULL_paths_to_scan(starting_folder="C:\\"):
    elements = os.listdir(starting_folder)
    for element in elements:
        full_path = os.path.join(starting_folder, element)
        if os.path.isfile(full_path):
            csv_add_path(full_path)
        else:
            FULL_paths_to_scan(full_path)


# QUICK SCANNING
def QUICK_files_to_scan():
    pass
