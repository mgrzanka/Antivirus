from typing import Optional

from crontab import CronTab, CronItem
import os

from .JsonFile import JsonFile
from .get_user_name import get_user_name


class Cron:
    '''
    A class used to adjust required cronjobs

    Attributes
    -----------
    json_file: JsonFile
        handler to JsonFile class instance

    Properties
    ------------
    username: str
        name of antivirus user
    interval: int
        time interval between two quickscans
    path_to_touch: str
        path where cronjob should create file
    command: str
        command of the cronjob

    Methods
    -----------
    find_CronJob(crontab_file: Crontab): returns job or None
        Checks if program-running user has required cronjob
    create_cronjob(crontab_file: CronTab): returns nothing
        Creates new, required cronjob
    update_minutes(crontab_file: Crontab, scan_job: CronItem): returns nothing
        Updates minutes of cronjob
    scan_cron_configuration()
        Configure required cronjob based on its current status

    Uses Crontab
    '''
    def __init__(self, json_file: JsonFile) -> None:
        '''
        json_file: JsonFile
            handler to JsonFile class instance
        '''
        self._json_file = json_file

    @property
    def username(self) -> str:
        '''name of antivirus user
        str
        '''
        return get_user_name()

    @property
    def interval(self) -> int:
        '''time interval between two quickscans
        int
        '''
        return self._json_file.quickscan_interval

    @property
    def path_to_touch(self) -> str:
        '''path where cronjob should create file
        str
        '''
        home_folder = os.path.join("/home", self.username)
        program_folder = os.path.join(home_folder, "Antivirus")
        return os.path.join(program_folder, "DoQuickscan")

    @property
    def command(self) -> str:
        '''command of the cronjob
        str
        '''
        return f'touch {self.path_to_touch}'

    def find_CronJob(self, crontab_file: CronTab) -> Optional[CronItem]:
        ''' Checks if program-running user has required cronjob

        If the program-running user has cronjob with required command, return this job
        If he doesn't, return None

        Returns cronjob or None

        Parameters
        -------------
        crontab_file: CronTab
            crontab file for program-running user
        '''
        for job in crontab_file:
            if job.command == self.command:
                return job
        return None

    def create_cronjob(self, crontab_file: CronTab) -> None:
        '''Creates new, required cronjob

        Returns nothing

        Parameters
        -------------
        crontab_file: CronTab
            crontab file for program-running user
        '''
        scan_job = crontab_file.new(command=self.command)
        scan_job.setall(f'*/{self.interval} * * * ')
        crontab_file.write()

    def update_minutes(self, crontab_file: CronTab, scan_job: CronItem) -> None:
        '''Updates minutes of cronjob

        Returns nothing

        Parameters
        -------------
        crontab_file: CronTab
            crontab file for program-running user
        scan_job: CronItem
            represents cronjob resposible for quickscan
        '''
        scan_job.setall(f'*/{self.interval} * * * ')
        crontab_file.write()

    def scan_cron_configuration(self) -> None:
        ''' Configure required cronjob

        If program-running user doesn't have cronjob that creates DoMessage file,
            create it
        If the program-running user has the cronjob, but with wrong time configuration,
            update it
        If everything is set, do nothing

        Returns nothing

        Parameters
        -------------
        None
        '''
        scan_cron = CronTab(self.username)
        scan_job = self.find_CronJob(scan_cron)
        if not scan_job:
            self.create_cronjob(scan_cron)
        elif scan_job.minute != self.interval:
            self.update_minutes(scan_cron, scan_job)
