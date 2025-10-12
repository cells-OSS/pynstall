from time import sleep
import shutil
import subprocess
import os
import sys
import ctypes
import tempfile
import requests
from packaging import version

__version__ = "v1.2"


def get_latest_release_tag():
    try:
        url = "https://api.github.com/repos/cells-OSS/pynstaller/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print("Failed to check for updates:", e)
        return __version__.lstrip("v")


def is_update_available(current_version):
    latest = get_latest_release_tag()
    return version.parse(latest) > version.parse(current_version.lstrip("v"))


def download_latest_script():
    latest_version = get_latest_release_tag()
    filename = f"pynstaller-v{latest_version}.py"
    url = "https://raw.githubusercontent.com/cells-OSS/pynstaller/main/pynstaller.py"
    response = requests.get(url)
    lines = response.text.splitlines()
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")
    print(
        f"Current version: {__version__}, Latest: v{get_latest_release_tag()}")
    print(
        f"Downloaded update as '{filename}'. You can now safely delete the old version.")

    input("Press Enter to exit...")
    exit()

def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False
    
if not _is_admin():
    print("Requesting admin privileges...")
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def install_chocolatey():
    installationScript = (
        'Set-ExecutionPolicy Bypass -Scope Process -Force; '
        '[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))'
    )

    if _is_admin():
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", installationScript],
            check=True
        )
        return

    fd, script_path = tempfile.mkstemp(suffix=".ps1", text=True)
    os.close(fd)
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(installationScript)

    ps_cmd = (
        "Start-Process powershell -Verb RunAs -ArgumentList "
        "'-NoProfile','-ExecutionPolicy','Bypass','-File','{}' -Wait"
    ).format(script_path.replace("'", "''"))

    subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_cmd], check=True)

    try:
        os.remove(script_path)
    except OSError:
        pass

def get_choco_cmd():
    return shutil.which("choco") or r"C:\ProgramData\chocolatey\bin\choco.exe"

if os.path.exists("auto_update.conf"):
                if is_update_available(__version__):
                    print("New version available!")
                    download_latest_script()

if os.path.exists("welcome_message.conf"):
    with open("welcome_message.conf", "r", encoding="utf-8") as f:
        welcome_message = f.read()
else:
    welcome_message = """
===================================================
                     pynstaller
WARNING: The names of the apps are separated
like "app1;app2;app3" unless specified otherwise.
===================================================
"""

menu = """
1 = Install an app
2 = Create a profile
3 = Run a profile
4 = Settings

TIP: To come back to this menu at any time, just type "back".
"""

print(welcome_message, menu)

chooseOption = input("Which option would you like to choose(1/2/3)?: ")

if chooseOption == "1":

    whichApp = input("Type the name of the app(s) you want to install: ")

    if whichApp.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    print("Installing Chocolatey...")

    sleep(2)

    if os.path.exists(get_choco_cmd()):
        print("Chocolatey is already installed.")
    else:
        install_chocolatey()

    print(f"Installing {whichApp}...")

    sleep(2)

    choco = get_choco_cmd()
    subprocess.run([choco, "install", whichApp, "-y"], check=True)

if chooseOption == "2":

    profileName = input("Type the name of the profile you want to create: ")

    if profileName.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    with open(f"{profileName}.conf", "w") as profileFile:
        appNames = input(
            "Type the names of the apps you want to add to the profile (separated by commas): ")
        for appName in appNames.split(","):
            profileFile.write(appName.strip() + "\n")

    print(f"Your profile '{profileName}.conf' has been created successfully.")

if chooseOption == "3":
    inputProfileName = input("Type the name of the profile you want to run: ")

    if inputProfileName.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if os.path.exists(f"{inputProfileName}.conf"):
        print("Checking if Chocolatey is installed...")
        
        sleep(2)

        if os.path.exists(get_choco_cmd()):
            print("Chocolatey is already installed.")
        else:
            print("Chocolatey is not installed. Installing Chocolatey...")

            sleep(2)

            install_chocolatey()

        print(f"Installing apps from profile '{inputProfileName}.conf'...")

        sleep(2)

        with open(f"{inputProfileName}.conf", "r") as profileFile:
            for line in profileFile:
                appName = line.strip()
                if appName:
                    print(f"Installing {appName}...")
                    subprocess.run(
                        ["choco", "install", appName, "-y"], check=True)

        print("All apps from the profile have been successfully installed.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        print(f"Profile '{inputProfileName}.conf' does not exist.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

if chooseOption == "4":
    settings_menu = """
===================================================
                     Settings
    1 = Turn Auto Update On/Off
    2 = Change Welcome Message
    3 = Reset Welcome Message
    4 = Figlet Welcome Message
===================================================
    """

    print(settings_menu)

    settingOption = input("Which setting would you like to change(1/2/3/4)?: ")
    if settingOption.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    if settingOption == "1":
        autoUpdateMenu = """
===================================================
                     Auto Update
    1 = Enable Auto Updates
    2 = Disable Auto Updates
===================================================
    """

        print(autoUpdateMenu)

        autoUpdateOption = input("Which option would you like to choose(1/2)?: ")

        if autoUpdateOption.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        if autoUpdateOption == "1":
            print("Enabling Auto Updates...")
            with open("auto_update.conf", "wb") as autoUpdateFile:
                autoUpdateFile.write("True".encode())
            print("Auto Updates have been enabled successfully!")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        
        if autoUpdateOption == "2":
            print("Disabling Auto Updates...")
            if os.path.exists("auto_update.conf"):
                os.remove("auto_update.conf")
                print("Auto Updates have been disabled successfully!")
                input("Press Enter to continue...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("Auto Updates are already disabled.")
                input("Press Enter to continue...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
    if settingOption == "2":
        welcome_messageMenu = """
============================================
        Change Welcome Message
============================================            
"""
        print(welcome_messageMenu)
        new_welcome_message = input(
            "New welcome message(use \\n for new lines): ")
        with open("welcome_message.conf", "w", encoding="utf-8") as f:
            f.write(new_welcome_message.replace("\\n", "\n"))
        print("Welcome message updated.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if settingOption == "3":
        if os.path.exists("welcome_message.conf"):
            os.remove("welcome_message.conf")
            print("Welcome message has been reset to default.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Welcome message is already the default.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

    if settingOption == "4":
        print("This feature is coming soon!")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        print("Invalid choice.")
        input("Press Enter to continue...")


else:
    print("Invalid choice.")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)