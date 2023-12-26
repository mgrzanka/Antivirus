import tkinter
import os
import subprocess
from abc import abstractmethod


class Message:
    def __init__(self, old_path, new_path) -> None:
        self._old_path = old_path
        self._new_path = new_path
      
    @abstractmethod
    def create_label(self, window):
        pass

    def delete(self, main_window):
        window = tkinter.Tk()
        window.geometry("400x150")
        window.title("Antivirus Message")
        try:
            os.remove(self._new_path)
            text = "Malicious file was deleted"
            command = lambda: [main_window.destroy(), window.destroy()]
        except Exception:
            text = "Error occured while deleting the malicious file"
            command = window.destroy
        label = tkinter.Label(window, text=text, font=("Arial", 12))
        button = tkinter.Button(window, text="OK", font=("Arial", 12), command=command)
        label.pack(pady=20)
        button.pack(pady=10)
        window.mainloop()

    def explore_file(self):
        if os.path.exists(self._new_path):
            path = os.path.split(self._new_path)
        else:
            path = os.path.split(self._old_path)
        file = path[1]
        dir = path[0]
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {dir} && ls | grep {file}; exec bash"])

    def delete_button(self, window, frame):
        frame.columnconfigure([2], weight=1)

        command = lambda: self.delete(window)
        delete_button = tkinter.Button(frame, text="Delete", font=("Arial", 14), command=command)
        delete_button.grid(row=0, column=2, sticky=tkinter.W+tkinter.E)

    def display_message(self):
        window = tkinter.Tk()
        window.geometry("550x275")
        window.title("Antivirus Message")
        
        title_label = tkinter.Label(window, text=f"WARNING\nVirus found at: {self._old_path}", font=('Arial', 16))
        dash_line = tkinter.Label(window, text="-"*100, font=("Arial", 16))
        
        frame = tkinter.Frame(window)
        frame.columnconfigure([0], weight=1)
        frame.columnconfigure([1], weight=1)
        
        command = self.explore_file
        explore_button = tkinter.Button(frame, text="Explore", font=("Arial", 14), command=command)
        explore_button.grid(row=0, column=0, sticky=tkinter.W+tkinter.E)

        command = window.destroy
        cancel_button = tkinter.Button(frame, text="Cancel", font=("Arial", 14), command=command)
        cancel_button.grid(row=0, column=1, sticky=tkinter.W+tkinter.E)

        self.delete_button(window, frame)

        title_label.pack(pady=8)
        dash_line.pack()
        self.create_label(window)
        frame.pack(pady=10, fill='x')

        window.mainloop()


class SuccessMessage(Message):
    def create_label(self, window):
        text = f'''Permissions of the file were deleted.
    It was successfuly moved to\n{self._new_path}\n\nWhat do you want to do?'''
        label = tkinter.Label(window, text=text, font=('Arial', 14))
        label.pack(padx=10)


class PermissionErrorMessage(Message):
    def create_label(self, window):
        text = f'''No permission to change file to unexecutable
    Moved it to: {self._new_path}\n\nWhat do you want to do?'''
        label = tkinter.Label(window, text=text, font=("Arial", 14))
        label.pack(padx=10)


class FailureMessage(Message):
    def create_label(self, window):
        text = f'''Couldn't quaranteen the file
    It's still at: {self._old_path}\n\nWhat do you want to do?'''
        label = tkinter.Label(window, text=text, font=("Arial", 14))
        label.pack(padx=10)

    def delete_button(self, window, frame):
        pass