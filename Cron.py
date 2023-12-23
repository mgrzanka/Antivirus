from crontab import CronTab
import os

from JsonFile import JsonFile

main_folder = "/home/gosia/Antivirus"


class Cron:  
    def scan_cron_configuration(json_file: JsonFile):
        scan_cron = CronTab(os.environ.get('USER'))
        cron_path = os.path.join(main_folder, "ScanMessage.txt")
        command = f'echo "Cron message: do a scan!" > {cron_path}'
        scan_job = Cron.find_CronJob(scan_cron, command)
        if not scan_job:
            scan_job = scan_cron.new(command=command)
            scan_job.setall(f'*/{json_file.quickscan_interval} * * * ')
            scan_cron.write()
            return
        elif scan_job.minute != f"*/{json_file.quickscan_interval}":
            scan_job.setall(f'*/{json_file.quickscan_interval} * * * ')
            scan_cron.write()
            scan_job
            return
    
    def reboot_cron_configuration():
        scan_cron = CronTab(os.environ.get('USER'))
        command = f'python3 /home/gosia/Antyvirus/test.py'
        scan_job = Cron.find_CronJob(scan_cron, command)
        if not scan_job:
            scan_job = scan_cron.new(command=command)
            scan_job.every_reboot()
            scan_cron.write()
    
    @staticmethod
    def find_CronJob(scan_cron: CronTab, command):
        for job in scan_cron:
            if job.command == command:
                return job
        return None