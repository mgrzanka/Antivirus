from configuration_code.Cron import Cron
from configuration_code.Startup import Startup
from configuration_code.get_user_name import get_user_name

from unittest.mock import Mock
from crontab import CronTab
import os


def test_cron():
    # Assert interval
    json_file = Mock(quickscan_interval=2)
    cron = Cron(json_file)
    assert cron.interval == 2

    # Check creation of cronjob
    crontab_file = CronTab(get_user_name())
    cronjob = [job for job in crontab_file if job.command == cron.command]
    cron.create_cronjob(crontab_file)
    assert cronjob is not None
    assert cron.find_CronJob(crontab_file) is not None

    # Check update minutes
    json_file.quickscan_interval = 3
    cronjob = cronjob[0]
    cron.update_minutes(crontab_file, cronjob)
    assert cronjob.minute == '*/3'
    assert cron.interval == 3
# You might want to remove this additional crontabs from your user crontabs


# Startup tests

def test_auto_startup():
    username = get_user_name()
    # Assert properties
    json_file = Mock(interpreter_path="/interpreter/path")
    auto_startup = Startup(json_file)
    assert auto_startup.interpreter_path == "/interpreter/path"
    assert auto_startup.python_script_path == f"/home/{username}/Antivirus/reboot.py"
    assert auto_startup.desktop_file_path == f"/home/{username}/.config/autostart/reboot.desktop"

    # Check creation
    if os.path.exists(auto_startup.desktop_file_path):
        os.remove(auto_startup.desktop_file_path)
    json_file.reboot = True
    auto_startup.configure_startup()
    assert auto_startup.is_configured is True

    # Check removal
    json_file.reboot = False
    auto_startup.configure_startup()
    assert auto_startup.is_configured is False
