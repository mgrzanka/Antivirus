# imports
from csv_heap_management import (FULL_paths_to_scan, csv_add_path,
                                 csv_delete_path, if_empty)
# from csv_heap_management import QUICK_files_to_scan
from malware_checking import check_by_executable, check_by_MD5, check_by_API

from queue import Queue, Empty
from threading import Thread, Event
from csv import DictReader
from time import time, sleep

# Global variables
input_queue = Queue()
output_queue = Queue()
API_key = "5436aa834925d0d29afcaac72f5dffabf1a27a6c95a6447ae51b3b4bcbbfaaa0"


# Function summing up all checkings
# returns path if file's in MD5 database, else return None
def check_file(file):
    path, hash = file["path"], file["hash"]
    if check_by_executable(path):
        if check_by_MD5(hash):
            return path
        else:
            input_queue.put(path)
            return None
    else:
        return None


def api_thread_function(event: Event, previous_time: int):
    while True:
        if event.is_set():
            break
        if not input_queue.empty():
            since_last_api = time() - previous_time
            if since_last_api < 240:
                sleep(240-since_last_api)
            previous_time = time()
        try:
            path = input_queue.get(timeout=1)
        except Empty:
            continue
        if check_by_API(path, API_key):
            output_queue.put(path)
        input_queue.task_done()


def scan_file():
    viruses = []
    event = Event()
    with open("scan_heap", "r") as scan_heap:
        T = time() - 240
        api_thread = Thread(target=api_thread_function, args=(event, T))
        api_thread.start()
        csv_reader = DictReader(scan_heap)
        for file in csv_reader:
            if check_file(file):
                viruses.append(file["path"])
            csv_delete_path()
        input_queue.join()
        event.set()
        api_thread.join()
        if not output_queue.empty():
            api_result = [virus for virus in output_queue.queue()]
            return viruses + api_result
        else:
            return viruses


def full_scan(starting_folder: str):
    csv_add_path("", True)
    FULL_paths_to_scan(starting_folder)
    detected_viruses = scan_file()
    return detected_viruses


def quick_scan():
    if if_empty():
        return
    detected_viruses = scan_file()
    return detected_viruses


path = "C:\\Users\\Gosia\\Studia\\Semestr 1\\PIPR\\Labolatoria\\pipr_lab\\Lab2"
print(full_scan(path))
