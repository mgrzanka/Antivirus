from messages_code.Messages import (PermissionErrorMessage,
                                    RebootMessage,
                                    SuccessMessage,
                                    FailureMessage)
from configuration_code.JsonFile import JsonFile
from configuration_code.get_user_name import get_user_name


username = get_user_name()


def test_PermissionErrorMessage():
    message = PermissionErrorMessage()
    message.display_message()


def test_RebootMessage():
    json_path = f"/home/{username}/Antivirus/settings.json"
    json_file = JsonFile(json_path)
    user_path = f"/home/{username}"
    message = RebootMessage(user_path, json_file)
    message.display_message()


def test_SuccessMessage_filedeleted():
    path = f"/home/{username}/Antivirus/test"
    new_path = f"/home/{username}/Antivirus/.quarantine/test"
    with open(new_path, 'w') as file:
        file.write("test")
    messsage = SuccessMessage(new_path, path)
    messsage.display_message()


def test_SuccessMessage_erroroccured():
    path = f"/home/{username}/Antivirus/test"
    new_path = f"/home/{username}/Antivirus/.quarantine/test"
    messsage = SuccessMessage(new_path, path)
    messsage.display_message()


def test_FailureMessage():
    path = f"/home/{username}/Antivirus/testt"
    new_path = f"/home/{username}/Antivirus/.quarantine/testt"
    with open(path, 'w') as file:
        file.write("test")
    message = FailureMessage(new_path, path)
    message.display_message()
