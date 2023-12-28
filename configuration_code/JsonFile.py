from argparse import ArgumentParser
from json import load


class JsonFile:
    def __init__(self, default_path: str) -> None:
        self._default_path = default_path

    def create_parser(self):
        parser = ArgumentParser(
            description=f'''
            "Run antivirus file with configuration file.
            Default: {self._default_path}'''
        )
        parser.add_argument('-c', '--config',
                            type=str,
                            default=self._default_path,
                            help="Ścieżka do pliku konfiguracyjnego")
        return parser.parse_args()

    @property
    def json_path(self):
        json_path = self.create_parser()
        json_path = json_path.config
        return json_path

    @property
    def interpreter_path(self):
        with open(self.json_path, 'r') as settings_file:
            json_data = load(settings_file)
            return json_data["Interpreter path"]
    
    @property
    def quickscan_interval(self):
        with open(self.json_path, "r") as settings_file:
            json_data = load(settings_file)
            return json_data["Quickscan time interval [minutes]"]

    @property
    def reboot(self):
        with open(self.json_path, "r") as settings_file:
            json_data = load(settings_file)
            return json_data["Reboot auto-start"]
    
    @property
    def folders_to_watch(self):
        with open(self.json_path, "r") as settings_file:
            json_data = load(settings_file)
            return json_data["Folders to watch"]