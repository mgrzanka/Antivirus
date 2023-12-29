from messages_code.Messages import RebootMessage
from configuration_code.get_user_name import get_user_name
from configuration_code.JsonFile import JsonFile

import os


def main():
    '''
    Program that will run on the reboot, displays reboot message, in which there is a button
    to launch antivirus main program
    '''
    username = get_user_name()
    user_path = os.path.join("/home", username)
    main_folder = os.path.join(user_path, "Antivirus")
    default_path = os.path.join(main_folder, 'settings.json')

    json_file = JsonFile(default_path)

    reboot_message = RebootMessage(user_path, json_file)
    reboot_message.display_message()


if __name__ == "__main__":
    main()
