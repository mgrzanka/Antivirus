from argparse import ArgumentParser
from json import load


class JsonFile:
    '''
    A class used to represent json file with program settings

    Attributes
    -------------
    default_path: str
        default path if there is no other path given in parser

    Properties
    --------------
    json_path: str
        path to settings file
        loaded from parser
    interpreter_path: str
        path to interpreter that is used to launch program
        loaded from settings json file
    quickscan_interval: int
        time in minutes how often do quickscan
        loaded from settings json file
    reboot: bool
        should program be launched automaticaly after system reboot
        loaded from settings json file
    folders_to_watch: list[str]
        list of folders program should monitor
        loaded from settings json file

    Methods
    -------------
    create_parser(): returns parsed argument values
        creates --config parser (a path to settings json file)
    '''
    def __init__(self, default_path: str) -> None:
        self._default_path = default_path
        self._json_path = None

    def create_parser(self, args=None):
        ''' creates parser to antivirus.py with possible -c flag taking a path to settings file

        Returns argparse.Namespace object that contains the parsed argument values
        The only argument supported is for flag -c or --config

        Parameters
        ------------
        None
        '''
        parser = ArgumentParser(
            description=f'''
            "Run antivirus file with configuration file.
            Default: {self._default_path}'''
        )
        parser.add_argument('-c', '--config',
                            type=str,
                            default=self._default_path,
                            help="Ścieżka do pliku konfiguracyjnego")
        return parser.parse_args(args)

    @property
    def json_path(self):
        ''' returns path to settings file, loaded from input data via parser
        str
        '''
        if not self._json_path:
            args = self.create_parser(['-c', self._default_path])
            self._json_path = args.config
        return self._json_path

    @property
    def interpreter_path(self):
        '''returns path to interpreter that is used to launch program, loaded from settings json
        file
        int
        '''
        with open(self.json_path, 'r') as settings_file:
            json_data = load(settings_file)
            return json_data["Interpreter path"]

    @property
    def quickscan_interval(self):
        '''returns time in minutes how often do quickscan, loaded from settings json file
        str
        '''
        with open(self.json_path, "r") as settings_file:
            json_data = load(settings_file)
            return json_data["Quickscan time interval [minutes]"]

    @property
    def reboot(self):
        '''returns if program should be launched automaticaly after system reboot,
        loaded from settings json file
        bool
        '''
        with open(self.json_path, "r") as settings_file:
            json_data = load(settings_file)
            return json_data["Reboot auto-start"]

    @property
    def folders_to_watch(self):
        '''returns list of folders program should monitor loaded from settings json file
        list[str]
        '''
        with open(self.json_path, "r") as settings_file:
            json_data = load(settings_file)
            return json_data["Folders to watch"]
