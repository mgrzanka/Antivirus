from configuration_code.JsonFile import JsonFile
from configuration_code.Cron import Cron
from configuration_code.Startup import Startup
from configuration_code.get_user_name import get_user_name

# from unittest.mock import Mock
from crontab import CronTab
import os
import json

# JsonFile tests


def test_json_data_loading():
    data = {
        "Interpreter path": "/home/gosia/venv/bin/python",
        "Quickscan time interval [minutes]": 2,
        "Reboot auto-start": True,
        "Folders to watch": [
            "/home/gosia/Antivirus",
            "/bin"
        ]
    }
    username = get_user_name()
    default_path = f"/home/{username}/Antivirus/tmp_settings.json"
    with open(default_path, 'w') as json_file:
        json.dump(data, json_file)
    json_file = JsonFile(default_path)
    assert json_file.json_path == default_path
    assert json_file.quickscan_interval == 2
    assert json_file.interpreter_path == "/home/gosia/venv/bin/python"
    assert json_file.reboot is True
    assert json_file.folders_to_watch == [
                "/home/gosia/Antivirus",
                "/bin"
            ]
    os.remove(default_path)

# Cronjob tests


def test_cron_configuration():
    username = get_user_name()
    default_path = f"/home/{username}/Antivirus/settings.json"
    json_file = JsonFile(default_path)
    Cron.scan_cron_configuration(json_file, username)

    cron_path = f"/home/{username}/Antivirus/DoQuickscan"
    user_cronjobs = CronTab(username)
    command = f'touch {cron_path}'
    scan_job = Cron.find_CronJob(user_cronjobs, command)

    assert scan_job.command == f'touch {cron_path}'
    assert scan_job.minute == f"*/{json_file.quickscan_interval}"


# Startup tests

def test_autostartup_configuration():
    username = get_user_name()
    user_path = os.path.join("/home", username)
    default_path = f"/home/{username}/Antivirus/settings.json"
    json_file = JsonFile(default_path)
    startup = Startup(json_file, user_path)

    startup.delete_startup()
    startup.is_configured is False
    startup.add_to_startup()
    startup.is_configured is True
