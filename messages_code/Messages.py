from typing import Optional

import tkinter
import os
import subprocess
from abc import abstractmethod, ABC

from configuration_code.JsonFile import JsonFile


class Message(ABC):
    '''
    An abstact class representing single Message to display for the user

    Attributes
    -------------
    window: tkinter.Tk
        Tk class instance representing system window
    frame: tkinter.Frame
        Frame class instance representing from for potential buttons on the window
    cancel_button: tkinter.Button
        Button class instance representing cancel button that every message will have

    Methods
    -------------
    create_labels(): abstractmethod, returns list[tkinter.Label]
        creates labels for message
    create_buttons(): abstractmethod, returns list[tkinter.Button]
        creates buttons for message
    display_message()
        puts every widget on the main window
    '''
    def __init__(self) -> None:
        '''
        window: tkinter.Tk
            Tk class instance representing system window
        frame: tkinter.Frame
            Frame class instance representing from for potential buttons on the window
        cancel_button: tkinter.Button
            Button class instance representing cancel button that every message will have
        '''
        self._window = tkinter.Tk()
        self._window.geometry("600x275")
        self._window.title("Antivirus Message")

        self._frame = tkinter.Frame(self._window)

        font = ("Arial", 14)
        self._cancel_button = tkinter.Button(self._frame, text="Cancel", font=font, command=self._window.destroy)

    @abstractmethod
    def create_labels(self) -> Optional[list[tkinter.Label]]:
        '''creates labels for message
        abstactmethod
        '''
        pass

    @abstractmethod
    def create_buttons(self) -> Optional[list[tkinter.Button]]:
        '''creates buttons for message
        abstactmethod
        '''
        pass

    def display_message(self) -> None:
        '''puts every widget on the main window
        Function gets list of labels and buttons to place from create_labels and
        create_buttons functions and places them on the window. It performs window
        mainloop.

        Atributes
        -----------
        None
        '''
        labels = self.create_labels()
        buttons = self.create_buttons()
        num_buttons = 0
        for label in labels:
            label.pack(pady=10)
        if buttons:
            for indx, button in enumerate(buttons):
                button.grid(row=0, column=indx, sticky=tkinter.W+tkinter.E)
                num_buttons += 1

        self._cancel_button.grid(row=0, column=num_buttons, sticky=tkinter.W+tkinter.E)
        self._frame.pack(pady=10, fill='x')
        self._window.mainloop()


class PermissionErrorMessage(Message):
    '''
    A class representing message that will apear when user runs program without sudo

    Attributes
    ------------
    inheritted from Message class, rewriten window geometry

    Methods
    ------------
    create_labels(): returns list[tkinter.Label]
        inherited, creates one label with required caption
    create_buttons(): returns list[tkinter.Label]
        inherited, creates space for cancel button
    '''
    def __init__(self) -> None:
        super().__init__()
        self._window.geometry("400x100")

    def create_labels(self) -> Optional[list[tkinter.Label]]:
        '''inherited, creates one label with required caption
        Returns list of one label

        Parameters
        ------------
        None
        '''
        font = ("Arial", 14)
        text = "You have to run the program with sudo :c"
        label = tkinter.Label(self._window, text=text, font=font)
        return [label]

    def create_buttons(self) -> Optional[list[tkinter.Button]]:
        '''inherited, creates space for cancel button
        Returns None

        Parameters
        ------------
        None
        '''
        self._frame.columnconfigure([0], weight=1)
        return None


class RebootMessage(Message):
    '''
    A class representing message that will apear at auto-reboot

    Attributes
    ------------
    json_file: JsonFile
        handler to settings jason file to get interpreter path
    user_path: str
        path to ~ of user running program

    Methods
    -----------
    launch_antivirus(windw: tkinter.Tk): returns nothing
        creates subprocess that run main antivirus program
    create_labels(): returns list[tkinter.Label]
        inherited, creates one label with required caption
    create_buttons(): returns list[tkinter.Label]
        inherited, creates launch button and space for cancel na launch buttons
    '''
    def __init__(self, user_path, json_file: JsonFile) -> None:
        '''
        json_file: JsonFile
            handler to settings jason file to get interpreter path
        user_path: str
            path to ~ of user running program
        '''
        super().__init__()
        self._json_file = json_file
        self._user_path = user_path
        self._window.geometry("700x200")

    def launch_antivirus(self, window: tkinter.Tk) -> None:
        '''creates subprocess that run main antivirus program
        Function that is run when launch button is clicked

        Returns nothing

        Parameters
        -----------
        window: tkinter.Tk
            represents system window of this message
        '''
        main_folder = os.path.join(self._user_path, "Antivirus")
        program_path = os.path.join(main_folder, "antivirus.py")
        interpreter_path = self._json_file.interpreter_path
        window.destroy()
        subprocess.run(["pkexec", interpreter_path, program_path])

    def create_labels(self) -> Optional[list[tkinter.Label]]:
        '''inherited, creates one label with required caption
        Returns list of one label

        Parameters
        ------------
        None
        '''
        font = ("Arial", 14)
        text = '''You have your Antivirus app installed and configured :)\n
        You can launch it anytime by typing 'sudo <interpreter_path> ~/Antivirus/antivirus'
        Do you want to launch scan and real-time protection now?'''
        label = tkinter.Label(self._window, text=text, font=font)
        return [label]

    def create_buttons(self) -> Optional[list[tkinter.Button]]:
        '''inherited, creates launch button and space for cancel na launch buttons
        Returns list of one button

        Parameters
        ------------
        None
        '''
        self._frame.columnconfigure([0], weight=1)
        self._frame.columnconfigure([1], weight=1)
        font = ("Arial", 14)

        def command():
            self.launch_antivirus(self._window)
        launch_button = tkinter.Button(self._frame, text="LAUNCH!", font=font, command=command)
        return [launch_button]


class SuccessMessage(Message):
    '''
    A class representing message that will apear after conducting a successful quarantine on
    infeted file and taking out its permissions

    Attributes
    ------------
    new_path: str
        new path to the file after quarantine
    old_path: str
        full path of malicious path

    Methods
    ---------
    delete(): returns nothing
        tries deleting malicious file and displays proper message (removal successful or not)
    explore_files(): returns nothing
        opens terminal at new_path path
    create_labels(): returns list[tkinter.Label]
        inherited, creates two labels with required caption
    create_buttons(): returns list[tkinter.Label]
        inherited, creates delete and explore buttons and space for cancel, delete
        and explore buttons
    '''
    def __init__(self, new_path: str, old_path: str) -> None:
        '''
        new_path: str
            new path to the file after quarantine
        old_path: str
            full path of malicious path
        '''
        super().__init__()
        self._new_path = new_path
        self._old_path = old_path

    def delete(self) -> None:
        '''tries deleting malicious file and displays proper message (removal successful or not)
        Function creates seperate tkinter window for displaying massage whether the removal
        was successful or not
        If it was successful, both new and main window are closed after clicking "OK"
        If it's not, main window stays open in case user want to explore the malicious file

        Returns nothing

        Parameters
        -----------
        None
        '''
        window = tkinter.Tk()
        window.geometry("400x150")
        window.title("Antivirus Message")
        try:
            os.remove(self._new_path)
            text = "Malicious file was deleted"

            def command():
                self._window.destroy()
                window.destroy()
        except Exception:
            text = "Error occured while deleting the malicious file"
            command = window.destroy
        label = tkinter.Label(window, text=text, font=("Arial", 12))
        button = tkinter.Button(window, text="OK", font=("Arial", 12), command=command)
        label.pack(pady=20)
        button.pack(pady=10)
        window.mainloop()

    def explore_file(self) -> None:
        '''opens terminal at new_path path
        Function opens terminal at new path and ls the name of the malicious file

        Returns nothing

        Parameters
        ------------
        None
        '''
        path = os.path.split(self._new_path)
        file = path[1]
        dir = path[0]
        subprocess.Popen(["x-terminal-emulator", "-e", f"cd {dir} && ls | grep {file}; exec bash"])

    def create_labels(self) -> Optional[list[tkinter.Label]]:
        '''inherited, creates two labels with required caption
        Returns list of two labels

        Parameters
        ------------
        None
        '''
        text1 = "WARNING"
        text2 = f'''Virus found at {self._old_path}\n
    Permissions of the file were deleted and it was successfuly moved to\n{self._new_path}\n
    What do you want to do?'''
        label1 = tkinter.Label(self._window, text=text1, font=('Arial', 16))
        label2 = tkinter.Label(self._window, text=text2, font=('Arial', 14))
        return [label1, label2]

    def create_buttons(self) -> Optional[list[tkinter.Button]]:
        '''inherited, creates delete and explore buttons and space for cancel, delete
        and explore buttons
        Returns list of two buttons

        Parameters
        ------------
        None
        '''
        self._frame.columnconfigure([0], weight=1)
        self._frame.columnconfigure([1], weight=1)
        self._frame.columnconfigure([2], weight=1)

        font = ("Arial", 14)
        delete_button = tkinter.Button(self._frame, text="Delete", font=font, command=self.delete)
        explore_button = tkinter.Button(self._frame, text="Explore", font=font, command=self.explore_file)
        return [delete_button, explore_button]


class FailureMessage(Message):
    '''
    A class representing a message that will apear after experiencing error in conducting
    a quarantine on infeted file and taking out its permissions

    Attributes
    -------------
    old_path: str
        full path of malicious path
    new_path: str
        full path of malicious file in quarantine where is was supposed to be placed

    Methods
    ------------
    explore_file(): return nothing
        opens terminal at either new_path or old_path path (depends where the file is)
    create_labels(): returns list[tkinter.Label]
        inherited, creates two labels with required caption
    create_buttons(): returns list[tkinter.Label]
        inherited, creates delete and explore buttons and space for cancel, delete and explore
        buttons
    '''
    def __init__(self, new_path: str, old_path: str) -> None:
        '''
        old_path: str
            full path of malicious path
        new_path: str
            full path of malicious file in quarantine where is was supposed to be placed
        '''
        super().__init__()
        self._window.geometry("600x200")
        self._old_path = old_path
        self._new_path = new_path

    def explore_file(self) -> None:
        '''opens terminal at either new_path or old_path path (depends where the file is)
        Function opens terminal at new or old path and ls the name of the malicious file

        Parameters
        ------------
        None
        '''
        if self._new_path:
            path = os.path.split(self._new_path)
        else:
            path = os.path.split(self._old_path)
        file = path[1]
        dir = path[0]
        subprocess.Popen(["x-terminal-emulator", "-e", f"cd {dir} && ls | grep {file}; exec bash"])

    def create_labels(self) -> Optional[list[tkinter.Label]]:
        '''inherited, creates two labels with required caption
        Returns list of two labels

        Parameters
        ------------
        None
        '''
        text1 = "WARNING"
        text2 = f'''Virus found at {self._old_path}\n
    Error occured while trying to quarantine. What do you want to do?'''
        label1 = tkinter.Label(self._window, text=text1, font=('Arial', 16))
        label2 = tkinter.Label(self._window, text=text2, font=('Arial', 14))
        return [label1, label2]

    def create_buttons(self) -> Optional[list[tkinter.Button]]:
        '''inherited, creates explore button and space for cancel and explore buttons
        Returns list of one button

        Parameters
        ------------
        None
        '''
        self._frame.columnconfigure([0], weight=1)
        self._frame.columnconfigure([1], weight=1)

        font = ("Arial", 14)
        explore_button = tkinter.Button(self._frame, text="Explore", font=font, command=self.explore_file)
        return [explore_button]
