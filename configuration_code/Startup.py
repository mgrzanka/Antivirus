import os

from .JsonFile import JsonFile
from .get_user_name import get_user_name


class Startup:
    '''
    A class used to adjust potential auto-startup on reboot

    Attributes
    -------------
    json_file: JsonFile
        handler to JsonFile class instance

    Properties
    --------------
    interpreter_path: str
        path to interpreter path
    python_script_path: str
        path to python script that will be ran at auto-startup
    desktop_file_path: str
        path to desktop file resposible for auto-startup
    desktop_file_content: str
        content of desktop file
    is_configured: bool
        return True if desktop_path exist, return False otherwise

    Methods
    -------------
    configure_startup(): returns nothing
        either removes or creates desktop file based on information from json
    '''
    def __init__(self, json_file: JsonFile) -> None:
        '''
        json_file: JsonFile
            handler to JsonFile class instance
        '''
        self._json_file = json_file

    @property
    def interpreter_path(self) -> str:
        '''path to interpreter path
        str
        '''
        return self._json_file.interpreter_path

    @property
    def should_exists(self) -> bool:
        '''returns wheter desktop file should be created
        bool
        '''
        return self._json_file.reboot

    @property
    def python_script_path(self) -> str:
        '''path to python script that will be ran at auto-startup
        str
        '''
        username = get_user_name()
        return os.path.join("/home", username, "Antivirus", "reboot.py")

    @property
    def desktop_file_path(self) -> str:
        '''path to desktop file resposible for auto-startup
        str
        '''
        username = get_user_name()
        return os.path.join("/home", username, ".config", "autostart", "reboot.desktop")

    @property
    def desktoop_file_content(self) -> str:
        '''content of desktop file
        str
        '''
        python_script_name = os.path.split(self.python_script_path)[1]
        return f'''[Desktop Entry]
Name={python_script_name}
Exec={self.interpreter_path} {self.python_script_path}
Type=Application
'''

    @property
    def is_configured(self) -> bool:
        '''return True if desktop_path exist, return False otherwise
        bool
        '''
        return os.path.exists(self.desktop_file_path)

    def configure_startup(self):
        '''either removes or creates desktop file based on information from json

        Returns nothing

        Parameters
        ------------
        None
        '''
        try:
            if not self.should_exists and self.is_configured:
                os.remove(self.desktop_file_path)
            elif self.should_exists and not self.is_configured:
                with open(self.desktop_file_path, 'w') as file:
                    file.write(self.desktoop_file_content)
        except Exception:
            pass
