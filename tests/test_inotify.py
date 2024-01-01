import pytest
import os
from threading import Thread
from unittest.mock import patch, Mock
from inotify_management_code.InotifyWatch import InotifyWatch
from configuration_code.get_user_name import get_user_name


@pytest.fixture
def standard_dir_watch():
    username = get_user_name()
    folder_path = "/path/to/folder"
    main_folder = f"/home/{username}/Antivirus"
    cron = False
    index = [Mock()]
    return InotifyWatch(folder_path, main_folder, cron, index)


def test_on_file_change_removal(standard_dir_watch):
    with patch('os.path.exists', return_value=False), \
            patch.object(standard_dir_watch._index[0], 'remove_file') as mock_remove_file:
        event = Mock(pathname="/example/path")
        standard_dir_watch.on_file_change(event)
        mock_remove_file.assert_called_with(event.pathname)


def test_on_file_change_file_creation_modification(standard_dir_watch):
    username = get_user_name()
    path = f"/home/{username}/Antivirus/file"
    with open(path, 'w') as file_handler:
        file_handler.write("#!")
    os.chmod(path, 0o744)
    event = Mock(pathname=path)
    with patch.object(standard_dir_watch._index[0], 'update_hash') as mock_update_hash:
        standard_dir_watch.on_file_change(event)
        mock_update_hash.assert_called()
    os.remove(path)


@pytest.fixture
def cronjob_file_watch():
    username = get_user_name()
    folder_path = "/path/to/folder"
    main_folder = f"/home/{username}/Antivirus"
    cron = True
    index = [Mock()]
    return InotifyWatch(folder_path, main_folder, cron, index)


def test_on_file_change_file_cronjob_file(cronjob_file_watch):
    username = get_user_name()
    path = f"/home/{username}/Antivirus/DoQuickscan"
    with open(path, 'w'):
        pass
    event = Mock(pathname=path)
    with patch.object(cronjob_file_watch._index[0], 'quickscan') as mock_quickscan:
        cronjob_file_watch.on_file_change(event)
        mock_quickscan.assert_called()


def test_watch_thread(cronjob_file_watch):
    thread = cronjob_file_watch.watch_thread()
    assert isinstance(thread, Thread)
