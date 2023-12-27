import os

class Startup:
    @property
    def is_configured(self):
        script_name = "reboot"
        path = f"/home/gosia/.config/autostart/{script_name}.desktop"
        return os.path.exists(path)

    def add_to_startup(self):
        if not self.is_configured:
            script_name = "reboot"
            script_path = "/home/gosia/Antivirus/reboot.py"
            interpreter_path = "/home/gosia/venv/bin/python"
            desktop_path = f"/home/gosia/.config/autostart/{script_name}.desktop"

            with open(desktop_path, 'w') as file:
                file.write(f'''[Desktop Entry]
Name={script_name}
Exec={interpreter_path} {script_path}
Type=Application
''')
