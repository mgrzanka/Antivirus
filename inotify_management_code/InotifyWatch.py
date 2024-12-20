import pyinotify
import os
import time
from threading import Thread

from file_management_code.FilesIndex import FilesIndex
from file_management_code.File import File


class InotifyWatch:
    '''
    A class used to represent an inotify watch for a given directory

    Attributes
    -------------
    folder_path: str
        full path to the folder being watched
    main_folder: str
        full path to the main folder of the program (Antivirus folder)
    cron: bool
        A flag telling whether the watch is for a file created by a cronjob
        or for the standard folder from the setting
    index: list[FileIndex]
        object representing index of files in watched folder
        it's a list, so cron watch can do a quickscan of all of the indexes
        if watch is not for cron, the list has just one element - watched folder index

    Methods
    --------------
    on_file_change(event: pyinotify.Event): returns nothing
        determines what to do when given in mask event occured
    watch_files(): returns nothing
        create watch for class instance's folder
    watch_thread(): returns Thread class instance
        starts thread of watch_files() function

    External libraries: pyinotify
    '''
    def __init__(self, folder_path: str, main_folder: str, cron: bool, index: list[FilesIndex]) -> None:
        '''
        folder_path: str
            full path to the folder being watched
        main_folder: str
            full path to the main folder of the program (Antivirus folder)
        cron: bool
            A flag telling whether the watch is for a file created by a cronjob
            or for the standard folder from the setting
        index: list[FileIndex]
            object representing index of files in watched folder
            it's a list, so cron watch can do a quickscan of all of the indexes
            if watch is not for cron, the list has just one element - watched folder index
        '''
        self._folder_path = folder_path
        self._cron = cron
        self._index = index
        self._main_folder = main_folder

    def on_file_change(self, event: pyinotify.Event) -> None:
        '''determines what to do when given in mask event occured
        If file is not cron file and it doesn't exist, it means the event was it's removal
        If the file was deleted, remove it from index
        If it was a file created by cronjob, do quickscan for all existing indexes
        and then remove cronjob file
        If it wasn't cronjob file: if it's binary, executable and not hidden,
        check if it's malicious
        If it's malicious, call file.quarantine() and remove it from index
        If it's not malicious, update it's hash in index (it changed so hash changed)

        Returns nothing

        Parameters
        -----------
        event: pyinotify.Event
            Event class instance containing information about event that occured
        '''
        cron_path = os.path.join(self._main_folder, "DoQuickscan")
        event_path = event.pathname

        # File deleted
        if not self._cron and event_path != cron_path and not os.path.exists(event_path):
            try:
                self._index[0].remove_file(event_path)
            except FileNotFoundError:
                pass

        # File created or modified
        if not os.path.isdir(event_path):
            file = File(event_path, self._main_folder)
            # Crone
            if file.path == cron_path and self._cron:
                if os.path.exists(cron_path):
                    print(f"{file.path} was created")
                    time.sleep(1)
                    for index in self._index:
                        index.quickscan()
                    os.remove(file.path)
                    return
                elif file.path != cron_path and self._cron:
                    return
            # Files
            else:
                try:
                    if not (file.is_binary() and file.is_executable()) or file.is_hidden():
                        return
                    if not self._cron:
                        if file.is_malicious():
                            file.quarantine_file()
                            self._index[0].remove_file(file.path)
                        else:
                            self._index[0].update_hash(file)
                            print(event_path)
                except FileNotFoundError:
                    pass

    def watch_files(self) -> None:
        '''create watch for class instance's folder
        Function creates pyinotify.WatchManager with different masks depending if it will watch
        cronjob-created file or normal directories. For normal directories, the watch is recursive
        It declares function on_file_change() to be event handler and creates inotifywatch,
        infinite loop

        Returns nothing

        Parameters
        -----------
        None
        '''
        watch_manager = pyinotify.WatchManager()
        if self._cron:
            mask = pyinotify.IN_CREATE
            watch_manager.add_watch(self._folder_path, mask=mask)
        else:
            mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_DELETE
            watch_manager.add_watch(self._folder_path, mask=mask, rec=True)

        event_handler = pyinotify.ProcessEvent()
        event_handler.process_default = self.on_file_change

        notifier = pyinotify.Notifier(watch_manager, event_handler)
        notifier.loop()

    def watch_thread(self) -> Thread:
        '''starts thread of watch_files() function
        Function create threading.Thread instance representing watch for single directory
        and starts it

        Returns thread instance so it can be stored in list in the main program for join()

        Parameters
        ------------
        None
        '''
        thread = Thread(target=self.watch_files)
        thread.start()
        return thread
