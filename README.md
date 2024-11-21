# Simple Antivirus

This project was developed as part of my **first-year coursework** at Warsaw University of Technology. It provides a basic antivirus solution that tracks and warns about suspicious files.

author: Małgorzata Grzanka
---


# Requirements
This program needs to be placed in a directory named Antivirus in ~ directory. It has to be ran with sudo. If it's not, the proper message will be displayed.

Packages:
This program requires following external libraries: pyinotify, crontab, chardet

# Configuration file
You need to include json file with required settings. You can either create your own and declare its location while running the code with the -c or --config argument. If no -c argument is given, program uses the default path (settings.json file). Settings should look like this:
- "Interpreter path": str,
- "Quickscan time interval [minutes]": int,
- "Reboot auto-start": bool,
- "Folders to watch": list[str]

# How to run
Run the program by typing: sudo (interpreter path with required packages) ~/Antivirus/antivirus.py [-c (json file path)]

# How does it work
Here is how a typical run of the antivirus looks like:
- When launched, antivirus performs a simple scan of included in settings.json directories
- If it comes accross a malicious file, it moves it to .quarantine folder and displays message that malicious file was detected (you can either delete it, explore its location or ignore this message)
- While scanning, it creates a index (.index.csv) for each directory that is being scanned of files that are binary, executable and not hidden. The index contains information about files' paths and hashes.
- After finishing the scan, antivirus watches given in settings.json directories for any modification or creation - if any of it takes place, program checks the file for malware and updates the index (if it's not malicious) or does what is in point 2 (if it's malicious)
- Once in a period of time given in settings.json, antivirus performs a quickscan for every directory in settings.json - it goes through every file in its index and checks if it's malware. If it is - look point 2, if it's not - it updates its hash in case it's out of date.


# Malware detection
Antivirus considers file infected if its hash matches a hash from known viruses hashes database (note: it can be uneffective in many cases). It uses https://github.com/CYB3RMX/MalwareHashDB.git database


# Auto-start at the reboot
You can enabl auto-start at the reboot in settings. When auto-started, program will be ran with default settings.


# Classes description
Cron: A class used to adjust required cronjobs. It creates cronjob for program user (if he doesn't have it already) that will create a DoQuickscan file in main folder once in a given in settings period of time. Creation of the file means that quickscan should be executed

get_user_name: A function that returns username of the user that has this antivirus installed. Function creates a list of all home directories. If the directory has Ativirus folder with antivirus.py app, it's considered program user's home directory

JsonFile: A class used to represent json file with program settings. Program gets values from settings by instance of this class.

Startup: A class used to adjust potential auto-startup on reboot by adding or removing desktop file from ~/.config/autostart

File: A class used to represent single file. It contains all file properties (path, hash, if it's executable / binary / hidden / malicious) and can be used to quarantine file

FileIndex: A class representing single index file. It's used to perform a scan / quickscan on the index and add / remove files from it. It also has a protection of running the program without sudo in create() method

InotifyWatch: A class used to represent an inotify watch for a given directory. It creates infinit loop to monitor any changes in this directory (recursively if it's for folders to watch, not recursively if it's for DoQuickscan file)

Message: An abstact class representing single Message to display for the user. Abstract methods are create_labels() and
create_buttons(), the display_message() method is used for every child class to display the message.

PermissionErrorMessage: A class representing message that will apear when user runs program without sudo

RebootMessage: A class representing message that will apear at auto-reboot

SuccessMessage: A class representing message that will apear after conducting a successful quarantine on infeted file and taking out its permissions

FailureMessage: A class representing a message that will apear after experiencing error in conducting a quarantine on infeted file and taking out its permissions