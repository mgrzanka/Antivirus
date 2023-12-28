import pyinotify
import os
import time
from threading import Thread

from file_management_code.FilesIndex import FilesIndex
from file_management_code.File import File


class InotifyWatch:
    def __init__(self, folder_path: str, main_folder, cron: bool, index: list[FilesIndex]) -> None:
        self._folder_path = folder_path
        self._cron = cron
        self._index = index
        self._main_folder = main_folder

    def on_file_change(self, event: pyinotify.Event):
        
        cron_path = os.path.join(self._main_folder, "ScanMessage.txt")
        event_path = event.pathname

        # File deleted
        if not self._cron and event_path != cron_path and not os.path.exists(event_path):
            try:
                self._index[0].remove_file(event_path)
            except FileNotFoundError:
                pass

        #File created or modified
        if not os.path.isdir(event_path):
            file = File(event_path, self._main_folder)
            # Crone
            if file.path == cron_path and self._cron:
                if os.path.exists(cron_path):
                    print(f"{file.path} was created")
                    os.remove(file.path)
                    time.sleep(1)
                    for index in self._index:
                        index.quickscan()                   
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

    def watch_file(self):
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

    def watch_thread(self):
        thread = Thread(target=self.watch_file)
        thread.start()
        return thread