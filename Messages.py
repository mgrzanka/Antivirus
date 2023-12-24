import tkinter

class Message:
    def __init__(self, content) -> None:
        self._content = content
    
    @property
    def content(self):
        return self._content
    
    def display_message(self):
        pass