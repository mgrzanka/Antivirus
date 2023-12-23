import os, json, csv

from JsonFile import JsonFile
from Cron import Cron
from InotifyWatch import InotifyWatch
from FilesIndex import FilesIndex


main_folder = "/home/gosia/Antivirus"


if __name__ == "__main__":
    if os.path.exists(os.path.join(main_folder, "ScanMessage.txt")):
        os.remove(os.path.join(main_folder, "ScanMessage.txt"))

    json_file = JsonFile(os.path.join(main_folder, "settings.json"))
    files_index = FilesIndex(os.path.join(main_folder, "index.csv"))

    Cron.scan_cron_configuration(json_file)
    if json_file.reboot:
        Cron.reboot_cron_configuration()
    
    folders_to_watch = json_file.folders_to_watch
    watches_list = []
    threads = []

    if not os.path.exists(files_index._path):
        files_index.create()

    for folder in folders_to_watch:
        folder_watch = InotifyWatch(folder, cron=False, index=files_index)
        watches_list.append(folder_watch)
        files_index.scan(folder)
    cron_watch = InotifyWatch(main_folder, cron=True, index=files_index)
    watches_list.append(cron_watch)

    for watch in watches_list:
        threads.append(watch.watch_thread())
    
    for thread in threads:
        thread.join()




