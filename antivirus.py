#!/usr/bin/env python3

import os

from JsonFile import JsonFile
from Cron import Cron
from InotifyWatch import InotifyWatch
from FilesIndex import FilesIndex

from Startup import Startup


main_folder = "/home/gosia/Antivirus"


if __name__ == "__main__":
    json_file = JsonFile(os.path.join(main_folder, "settings.json"))

    Cron.scan_cron_configuration(json_file)
    
    if json_file.reboot:
        startup = Startup()
        startup.add_to_startup()

    folders_to_watch = json_file.folders_to_watch
    watches_list = []
    indexes_list = []
    threads = []
    processes = []

    for folder in folders_to_watch:
        # Index for each folder
        files_index = FilesIndex(os.path.join(folder, ".index.csv"))
        indexes_list.append(files_index) # for crone, so it can scan all of the file indexes
        if not os.path.exists(files_index._path):
            files_index.create()
        processes.append(files_index.scan_process(folder))
        # Inotify watch for each folder
        folder_watch = InotifyWatch(folder, cron=False, index=[files_index])
        watches_list.append(folder_watch)
    
    for process in processes:
        process.join()

    cron_watch = InotifyWatch(main_folder, cron=True, index=indexes_list)
    watches_list.append(cron_watch)

    if os.path.exists(os.path.join(main_folder, "ScanMessage.txt")):
        os.remove(os.path.join(main_folder, "ScanMessage.txt"))

    for watch in watches_list:
        threads.append(watch.watch_thread())
    
    for thread in threads:
        thread.join()





