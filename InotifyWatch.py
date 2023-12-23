import pyinotify
import os
import csv
from threading import Thread

from FilesIndex import File, FilesIndex

main_folder = "/home/gosia/Antivirus"


class InotifyWatch:
    def __init__(self, folder_path: str, cron: bool, index: FilesIndex) -> None:
        self._folder_path = folder_path
        self._cron = cron
        self._index = index
    
    def on_file_change(self, event: pyinotify.Event):
        
        cron_path = os.path.join(main_folder, "ScanMessage.txt")
        event_path = event.pathname

        if not self._index.exclude_hidden(event_path, []):
            return
        
        if not os.path.isdir(event_path) and event_path != os.path.join(main_folder, "index.csv"):
            file = File(event_path)
            # Cron
            if file.path == cron_path and self._cron:
                print(f"{file.path} was created")
                self._index.scan(self._folder_path)
                os.remove(file.path)
            elif file.path != cron_path and self._cron:
                return
            # Pliki
            else:
                self._index.update_hash(file)
                print(event_path)

    def watch_file(self):
        watch_manager = pyinotify.WatchManager()
        if self._cron:
            mask = pyinotify.IN_CREATE
            watch_manager.add_watch(self._folder_path, mask=mask)
        else:
            mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY
            watch_manager.add_watch(self._folder_path, mask=mask, rec=True)

        event_handler = pyinotify.ProcessEvent()
        event_handler.process_default = self.on_file_change

        notifier = pyinotify.Notifier(watch_manager, event_handler)
        notifier.loop()
    
    def watch_thread(self):
        thread = Thread(target=self.watch_file)
        thread.start()
        return thread