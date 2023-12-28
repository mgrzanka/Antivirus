import tkinter
import os
import subprocess
from abc import abstractmethod, ABC


class Message(ABC):
    def __init__(self) -> None:
        self._window = tkinter.Tk()
        self._window.geometry("600x275")
        self._window.title("Antivirus Message")
        
        self._frame = tkinter.Frame(self._window)
        
        font = ("Arial", 14)
        self._cancel_button = tkinter.Button(self._frame, text="Cancel", font=font, command=self._window.destroy)
    
    @abstractmethod
    def create_labels(self):
        pass

    @abstractmethod
    def create_buttons(self):
        pass

    def display_message(self):
        labels = self.create_labels()
        buttons = self.create_buttons()
        num_buttons = 0
        for label in labels:
            label.pack(pady=10)
        for indx, button in enumerate(buttons):
            button.grid(row=0, column=indx, sticky=tkinter.W+tkinter.E)
            num_buttons += 1
        
        self._cancel_button.grid(row=0, column=num_buttons, sticky=tkinter.W+tkinter.E)
        self._frame.pack(pady=10, fill='x')
        self._window.mainloop()


class PermissionErrorMessage(Message):
    def __init__(self) -> None:
        super().__init__()
        self._window.geometry("400x100")
    
    def create_labels(self):
        font = ("Arial", 14)
        text = "You have to run the program with sudo :c"
        label = tkinter.Label(self._window, text=text, font=font)
        return [label]

    def create_buttons(self):
        self._frame.columnconfigure([0], weight=1)
        self._frame.columnconfigure([1], weight=1)
        font = ("Arial", 14)
        dir = '/home/gosia'
        command = lambda: subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {dir}; exec bash"])
        OK_button = tkinter.Button(self._frame, text="OK", font=font, command=command)
        return [OK_button]


class RebootMessage(Message):
    def __init__(self) -> None:
        super().__init__()
        self._window.geometry("600x200")
    
    def launch_antivirus(self, window):
        program_path = "/home/gosia/Antivirus/antivirus.py"
        interpreter_path = "/home/gosia/venv/bin/python"
        window.destroy()
        subprocess.run(["pkexec", interpreter_path, program_path])

    def create_labels(self):
        font = ("Arial", 14)
        text = '''You have your Antivirus app installed and configured :)\n
        You can launch it anytime by typing 'sudo ~/Antivirus/antivirus'
        Do you want to launch scan and real-time protection now?'''
        label = tkinter.Label(self._window, text=text, font=font)
        return [label]
    
    def create_buttons(self):
        self._frame.columnconfigure([0], weight=1)
        self._frame.columnconfigure([1], weight=1)
        font = ("Arial", 14)
        command = lambda: self.launch_antivirus(self._window)
        launch_button = tkinter.Button(self._frame, text="LAUNCH!", font=font, command=command)
        return [launch_button]


class SuccessMessage(Message):
    def __init__(self, new_path) -> None:
        super().__init__()
        self._new_path = new_path
    
    def delete(self):
        window = tkinter.Tk()
        window.geometry("400x150")
        window.title("Antivirus Message")
        try:
            os.remove(self._new_path)
            text = "Malicious file was deleted"
            command = lambda: [self._window.destroy(), window.destroy()]
        except Exception:
            text = "Error occured while deleting the malicious file"
            command = window.destroy
        label = tkinter.Label(window, text=text, font=("Arial", 12))
        button = tkinter.Button(window, text="OK", font=("Arial", 12), command=command)
        label.pack(pady=20)
        button.pack(pady=10)
        window.mainloop()
    
    def explore_file(self):
        path = os.path.split(self._new_path)
        file = path[1]
        dir = path[0]
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {dir} && ls | grep {file}; exec bash"])

    def create_labels(self):
        text1 = "WARNING"
        text2 = f'''Virus found at {self._old_path}\n
    Permissions of the file were deleted and it was successfuly moved to\n{self._new_path}\n\nWhat do you want to do?'''
        label1 = tkinter.Label(self._window, text=text1, font=('Arial', 16))
        label2 = tkinter.Label(self._window, text=text2, font=('Arial', 14))
        return [label1, label2]

    def create_buttons(self):
        self._frame.columnconfigure([0], weight=1)
        self._frame.columnconfigure([1], weight=1)
        self._frame.columnconfigure([2], weight=1)

        font = ("Arial", 14)
        delete_button = tkinter.Button(self._frame, text="Delete", font=font, command=self.delete)
        explore_button = tkinter.Button(self._frame, text="Explore", font=font, command=self.explore_file)
        return [delete_button, explore_button]


class FailureMessage(Message):
    def __init__(self, new_path, old_path) -> None:
        super().__init__()
        self._window.geometry("600x200")
        self._old_path = old_path
        self._new_path = new_path

    def create_labels(self):
        text1 = "WARNING"
        text2 = f'''Virus found at {self._old_path}\n
    Error occured while trying to quarantine. What do you want to do?'''
        label1 = tkinter.Label(self._window, text=text1, font=('Arial', 16))
        label2 = tkinter.Label(self._window, text=text2, font=('Arial', 14))
        return [label1, label2]
    
    def explore_file(self):
        if os.path.exists(self._new_path):
            path = os.path.split(self._new_path)
        else:
            path = os.path.split(self._old_path)
        file = path[1]
        dir = path[0]
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {dir} && ls | grep {file}; exec bash"])

    def create_buttons(self):
        self._frame.columnconfigure([0], weight=1)
        self._frame.columnconfigure([1], weight=1)

        font = ("Arial", 14)
        explore_button = tkinter.Button(self._frame, text="Explore", font=font, command=self.explore_file)
        return [explore_button]