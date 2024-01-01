import os
import sys

from configuration_code.JsonFile import JsonFile
from configuration_code.Cron import Cron
from configuration_code.Startup import Startup
from configuration_code.get_user_name import get_user_name

from inotify_management_code.InotifyWatch import InotifyWatch

from file_management_code.FilesIndex import FilesIndex


def main():
    '''
    Main program

    1. Get username of the program user (it's used to get paths of main_folder and
        default_path (for json))
    2. Create settings json file instance, updates cronjobs and auto-startup with
        information from json settings
    3. For each folder declared in json:
        - create files index instance, remove potential old index file and create new
        - if there is no sudo, exit the program (no permission message will be displayed)
        - start full scan process and add it to processes list
        - create watch for the folder and add it to watches list
    4. Wait for all the scan processes to end
    5. Create watch for the file created by cronjob and add it to watches list
    6. Remove created by cronjob file, so it can be created again and program can react
        to its creation
    7. Start eternal threads of inotify watches (the way how watches work is explained in
        InotifyWatch class)
    '''
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
        files_index = FilesIndex(os.path.join(folder, ".index.csv"), main_folder)
        indexes_list.append(files_index)
        files_index.create()
        if files_index.should_exit:
            if processes:
                for process in processes:
                    process.terminate()
                    sys.exit()
            else:
                sys.exit()
        processes.append(files_index.scan_process(folder))
        folder_watch = InotifyWatch(folder, main_folder, cron=False, index=[files_index])
        watches_list.append(folder_watch)

    for process in processes:
        process.join()

    cron_watch = InotifyWatch(main_folder, main_folder, cron=True, index=indexes_list)
    watches_list.append(cron_watch)

    if os.path.exists(os.path.join(main_folder, "DoQuickscan")):
        os.remove(os.path.join(main_folder, "DoQuickscan"))

    for watch in watches_list:
        threads.append(watch.watch_thread())

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
