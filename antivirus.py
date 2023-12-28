#!/home/gosia/venv/bin/python

import os

from configuration_code.JsonFile import JsonFile
from configuration_code.Cron import Cron
from configuration_code.Startup import Startup
from configuration_code.get_user_name import get_user_name

from inotify_management_code.InotifyWatch import InotifyWatch

from file_management_code.FilesIndex import FilesIndex


if __name__ == "__main__":
    username = get_user_name()

    user_path = f"/home/{username}"
    main_folder = os.path.join(user_path, 'Antivirus')
    default_path = os.path.join(main_folder, 'settings.json')
    
    json_file = JsonFile(default_path)
    Cron.scan_cron_configuration(json_file, username)
    startup = Startup(json_file, user_path)
    if json_file.reboot:
        startup.add_to_startup()
    else:
        startup.delete_startup()

    folders_to_watch = json_file.folders_to_watch
    watches_list = []
    indexes_list = []
    threads = []
    processes = []

    for folder in folders_to_watch:
        # Index for each folder
        files_index = FilesIndex(os.path.join(folder, ".index.csv"), main_folder)
        indexes_list.append(files_index) # for crone, so it can scan all of the file indexes
        if not os.path.exists(files_index._path):
            files_index.create()
        processes.append(files_index.scan_process(folder))
        # Inotify watch for each folder
        folder_watch = InotifyWatch(folder, main_folder, cron=False, index=[files_index])
        watches_list.append(folder_watch)
    
    for process in processes:
        process.join()

    cron_watch = InotifyWatch(main_folder, main_folder, cron=True, index=indexes_list)
    watches_list.append(cron_watch)

    if os.path.exists(os.path.join(main_folder, "ScanMessage.txt")):
        os.remove(os.path.join(main_folder, "ScanMessage.txt"))

    for watch in watches_list:
        threads.append(watch.watch_thread())
    
    for thread in threads:
        thread.join()




