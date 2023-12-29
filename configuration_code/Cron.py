from crontab import CronTab
import os

from .JsonFile import JsonFile


class Cron:
    '''
    A class used to adjust required cronjobs
    
    Attributes
    -----------
    None

    Methods
    -----------
    scan_cron_configuration(json_file, username)
        Configure required cronjob
    find_CronJob(scan_cron, command): returns job or None
        Checks if program-running user has required cronjob
    
    External libraries: crontab
    '''
    def scan_cron_configuration(json_file: JsonFile, username):
        ''' Configure required cronjob
        If program-running user doesn't have cronjob that creates DoMessage file, create it
        If the program-running user has the cronjob, but with wrong time configuration, update it
        If everything is set, do nothing

        Returns nothing

        Parameters
        -------------
        json_file: JsonFile
            handler to json with settings
        username: str
            program-running user username
        '''
        main_folder = f"/home/{username}/Antivirus"

        scan_cron = CronTab(username)
        cron_path = os.path.join(main_folder, "DoQuickscan")
        command = f'touch {cron_path}'
        scan_job = Cron.find_CronJob(scan_cron, command)
        if not scan_job:
            scan_job = scan_cron.new(command=command)
            scan_job.setall(f'*/{json_file.quickscan_interval} * * * ')
            scan_cron.write()
            return
        elif scan_job.minute != f"*/{json_file.quickscan_interval}":
            scan_job.setall(f'*/{json_file.quickscan_interval} * * * ')
            scan_cron.write()
            return

    @staticmethod
    def find_CronJob(scan_cron: CronTab, command):
        ''' Checks if program-running user has required cronjob
        If the program-running user has cronjob with required command, return this job
        If he doesn't, return None

        Returns cronjob or None
        
        Parameters
        -------------
        scan_cron: CronTab
            crontab file for program-running user
        command: str
            command in cronjob to look for
        '''
        for job in scan_cron:
            if job.command == command:
                return job
        return None