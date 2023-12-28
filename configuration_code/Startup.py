import os

from .JsonFile import JsonFile


class Startup:
    def __init__(self, json_file: JsonFile, user_path) -> None:
        main_folder = os.path.join(user_path, 'Antivirus')

        self._script_name = 'reboot'
        self._desktop_path = f"{user_path}/.config/autostart/{self._script_name}.desktop"
        self._interpreter_path = json_file.interpreter_path
        self._script_path = os.path.join(main_folder, 'reboot.py')

    @property
    def is_configured(self):
        return os.path.exists(self._desktop_path)

    def add_to_startup(self):
        if not self.is_configured:
            with open(self._desktop_path, 'w') as file:
                file.write(f'''[Desktop Entry]
Name={self._script_name}
Exec={self._interpreter_path} {self._script_path}
Type=Application
''')
    
    def delete_startup(self):
        if self.is_configured:
            try:
                os.remove(self._desktop_path)
            except FileNotFoundError:
                pass

