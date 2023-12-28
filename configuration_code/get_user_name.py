import os

def get_user_name():
    target_path = "Antivirus/antivirus.py"
    home_folder = "/home"
    subfolders = os.listdir(home_folder)
    users = [folder for folder in subfolders if os.path.isdir(os.path.join(home_folder, folder))]
    for user in users:
        full_path = os.path.join("/home", user, target_path)
        if os.path.exists(full_path):
            return user