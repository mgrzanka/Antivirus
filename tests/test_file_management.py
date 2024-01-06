from configuration_code.get_user_name import get_user_name
from file_management_code.File import File
from file_management_code.FilesIndex import FilesIndex

import os
import csv
import pytest
from unittest.mock import patch
from multiprocessing import Process

username = get_user_name()
main_folder = f"/home/{username}/Antivirus"


# File tests

def test_file_hashing():
    path = os.path.join(main_folder, "test_hash.txt")
    with open(path, 'w') as file:
        file.write("Hash testing")

    MD5_hash = "73aa28a22920299ca887a29af3b7049c"
    file = File(path, main_folder)
    assert file.hash == MD5_hash
    os.remove(path)


def test_is_binary():
    path = os.path.join(main_folder, "test_hash.txt")
    with open(path, 'w') as file:
        file.write("Binary testing")
    file = File(path, main_folder)
    assert file.is_binary() is False
    os.remove(path)

    with open(path, 'w') as file:
        file.write("#!")
    file = File(path, main_folder)
    assert file.is_binary() is True
    os.remove(path)


def test_is_executable():
    path = os.path.join(main_folder, "test_hash.txt")
    with open(path, 'w') as file:
        file.write("Executable testing")
    file = File(path, main_folder)
    assert file.is_executable() is False
    os.chmod(path, mode=0o700)
    assert file.is_executable() is True
    os.remove(path)


def test_is_hidden():
    path1 = os.path.join(main_folder, ".super_hidden.txt")
    with open(path1, 'w') as file:
        file.write("Hidden testing")
    file = File(path1, main_folder)
    assert file.is_hidden() is True
    os.remove(path1)
    path = os.path.join(main_folder, ".super_hidden")
    os.mkdir(path)
    path2 = os.path.join(path, "not_hidden.txt")
    file = File(path2, main_folder)
    assert file.is_hidden() is True
    os.rmdir(path)


def test_is_malicious():
    path = os.path.join(main_folder, ".super_hidden.txt")
    with open(path, 'w') as file:
        file.write("Malicious testing")
    file = File(path, main_folder)
    assert file.is_malicious() is False
    os.remove(path)


@pytest.fixture
def malicious_file():
    path = os.path.join(main_folder, "dont_move_me_please")
    quarantine_path = os.path.join(main_folder, ".quarantine")
    new_path = os.path.join(quarantine_path, "dont_move_me_please")
    with open(path, 'w'):
        pass
    return path, new_path, quarantine_path


def test_successful_quarantine(malicious_file):
    # If you click delete, error will apear, because it can't remove deleted file
    # (proves that the file was deleted :) )
    path, new_path, quarantine_path = malicious_file

    file = File(path, main_folder)
    file.quarantine_file()

    files = [file for file in os.listdir(quarantine_path)]
    assert "dont_move_me_please" in files

    os.remove(new_path)


def test_failure_quarantine(malicious_file):
    path, new_path, quarantine_path = malicious_file

    file = File(path, main_folder)

    with patch("shutil.move", side_effect=Exception("Mocked exception")):
        with patch("os.chmod", side_effect=Exception("Mocked exception")):
            file = File(path, main_folder)
            file.quarantine_file()
    os.remove(path)


# FileIndex tests


def test_create_no_need_sudo():
    path = os.path.join(main_folder, "index.csv")
    files_index = FilesIndex(path, main_folder)
    files_index.create()
    assert os.path.exists(path)


def test_create_need_sudo():
    # It should display no sudo message
    path = "/bin/.index.csv"
    files_index = FilesIndex(path, main_folder)
    files_index.create()


def test_remove_update_index():
    index_path = os.path.join(main_folder, "index.csv")
    file_path = os.path.join(main_folder, "test.txt")
    with open(file_path, 'w'):
        pass
    files_index = FilesIndex(index_path, main_folder)
    file = File(file_path, main_folder)
    files_index.create()

    # Add file to index
    files_index.update_hash(file)
    with open(index_path, 'r') as index_file:
        reader = csv.DictReader(index_file)
        data = list(reader)
    paths = [line["path"] for line in data]
    hashes = [line["hash"] for line in data]
    assert file_path in paths
    assert file.hash in hashes

    # Change content = change hash
    with open(file_path, 'w') as test_file:
        test_file.write("Test")
    assert file.hash not in hashes

    # Update hash
    files_index.update_hash(file)
    with open(index_path, 'r') as index_file:
        reader = csv.DictReader(index_file)
        data = list(reader)
    hashes = [line["hash"] for line in data]
    assert file.hash in hashes

    # Remove file from index
    files_index.remove_file(file.path)
    with open(index_path, 'r') as index_file:
        reader = csv.DictReader(index_file)
        content = [line["path"] for line in reader]
    assert file_path not in content

    os.remove(index_path)
    os.remove(file_path)


def test_scan():
    index_path = os.path.join(main_folder, "index.csv")
    index_file = FilesIndex(index_path, main_folder)
    index_file.create()

    file_path = f"/home/{username}/Antivirus/test.py"
    lines = ["#!/usr/bin/env python3\n\n",
             "print('Hello World')"]
    with open(file_path, 'w') as test_file:
        test_file.writelines(lines)
    os.chmod(file_path, 0o744)

    index_file.scan(main_folder)

    with open(index_path, 'r') as index:
        reader = csv.DictReader(index)
        content = list(reader)
        paths = [path["path"] for path in content]

    assert file_path in paths

    os.remove(file_path)
    os.remove(index_path)


def test_quickscan():
    # Adding file to the index
    index_path = os.path.join(main_folder, "index.csv")
    index_file = FilesIndex(index_path, main_folder)
    index_file.create()

    file_path = f"/home/{username}/Antivirus/test.py"
    file = File(file_path, main_folder)
    lines = ["#!/usr/bin/env python3\n\n",
             "print('Hello World')\n"]
    with open(file_path, 'w') as test_file:
        test_file.writelines(lines)
    os.chmod(file_path, 0o744)
    index_file.scan(main_folder)

    # Modifying file from the index
    with open(file_path, 'a') as test_file:
        test_file.write("print('Modification')")
    # Quickscanning
    index_file.quickscan()

    with open(index_path, 'r') as index:
        reader = csv.DictReader(index)
        content = list(reader)
        paths = [line["path"] for line in content]
        hashes = [line["hash"] for line in content]

    assert file.path in paths
    assert file.hash in hashes

    os.remove(file_path)
    os.remove(index_path)


def test_scan_proces():
    index_path = os.path.join(main_folder, "index.csv")
    index_file = FilesIndex(index_path, main_folder)
    index_file.create()
    proces = index_file.scan_process(main_folder)
    assert isinstance(proces, Process)
