import os

from .JsonFile import JsonFile


class Startup:
    '''
    A class used to adjust potential auto-startup

    Attributes
    -------------
    script_name: str
        name of the desktop file configuring auto-statrup
    desktop_path: str
        path to the desktop file configuring auto-statrup
    interpreter_path: str
        path to interpreter that is used to launch program in auto-startup
    script_path: str
        path to the program that will be launched in auto-startup
    
    Properties
    --------------
    is_configured: bool
        return True if desktop_path exist, return False otherwise
    
    Methods
    -------------
    add_to_startup(): returns nothing
        adds desktop file to ~/.config/autostart
    delete_startup(): returns nothing
        removes desktop file from ~/.config/autostart 
    '''
    def __init__(self, json_file: JsonFile, user_path) -> None:
        '''
        Parameters
        ------------
        script_name: str
            name of the desktop file configuring auto-startup
        desktop_path: str
            path to the desktop file configuring auto-startup
        interpreter_path: str
            path to interpreter that is used to launch program in auto-startup
        script_path: str
            path to the program that will be launched in auto-startup
    
        '''
        main_folder = os.path.join(user_path, 'Antivirus')

        self._script_name = 'reboot'
        self._desktop_path = f"{user_path}/.config/autostart/{self._script_name}.desktop"
        self._interpreter_path = json_file.interpreter_path
        self._script_path = os.path.join(main_folder, 'reboot.py')

    @property
    def is_configured(self):
        '''return True if desktop_path exist, return False otherwise
        bool
        '''
        return os.path.exists(self._desktop_path)

    def add_to_startup(self):
        ''' adds desktop file to ~/.config/autostart if it's not there
        Dekstop file contains: 
            - name of the aplication: reboot
            - launch command: interpreter_path script_path
            - application type: Aplication
        
        Returns nothing
        
        Parameters
        ------------
        None
        '''
        if not self.is_configured:
            with open(self._desktop_path, 'w') as file:
                file.write(f'''[Desktop Entry]
Name={self._script_name}
Exec={self._interpreter_path} {self._script_path}
Type=Application
''')
    
    def delete_startup(self):
        ''' removes desktop file from ~/.config/autostart if it's there

        Returns nothing

        Parameters
        -------------
        None
        '''
        if self.is_configured:
            try:
                os.remove(self._desktop_path)
            except FileNotFoundError:
                pass

