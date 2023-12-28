from file_management_code.FilesIndex import FilesIndex
from file_management_code.File import File
from Messages.Messages import SuccessMessage, PermissionErrorMessage, RebootMessage, FailureMessage
from configuration.Startup import Startup

import os
import stat
import csv


main_folder = "/home/gosia/Antivirus"


def test_update_hash():
    file = File("/home/gosia/elo.txt")
    file_index = FilesIndex("/home/gosia/Antivirus/index.csv")
    file_index.update_hash(file)


def funckcja(file_path, elements):
    path, element = os.path.split(file_path)
    if path and element:
        elements.append(element)
        funckcja(path, elements)
    else:
        elements.append(element)
    
    for element in elements:
        if '.' in element:
            elements = None
            return elements


def test_binary():
    file_path = "/home/gosia/Antivirus/antivirus.py"
    file = File(file_path)
    assert file.is_executable() == True
    assert file.is_binary() == True

def test_remove_file():
    index = FilesIndex("/home/gosia/Antivirus/.index.csv")
    file = File("/home/gosia/Antivirus/aha.py")
    index.remove_file(file.path)
    with open(index._path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
    assert len(rows) == 2

def test_move_file():
    path = '/home/gosia/elo.txt'
    destination_path = "/home/gosia/Antivirus/.quaranteen"
    file = File(path)
    file.quaranteen_file()
    new_file_path = os.path.join(destination_path, os.path.split(path)[1])
    # Pobierz informacje o pliku
    file_info = os.stat(new_file_path)
    # Wydziel uprawnienia
    permissions = stat.filemode(file_info.st_mode)
    assert permissions == '----------'

def test_create_window():
    path = "/home/gosia/Antivirus/.quaranteen/siema.txt"
    message = SuccessMessage("/home/gosia/siema.txt", path)
    message.display_message()

def test_quaranteen_file():
    file = File('/home/gosia/xd.txt')
    file.quaranteen_file()

def test_add_to_startup():
    start = Startup()
    start.add_to_startup()

def test_reboot_message():
    reboot_message = FailureMessage('/home/gosia/Antivirus/siema.txt', '/home/gosia/Antivirus/.quaranteen/siema.txt')
    reboot_message.display_message()





