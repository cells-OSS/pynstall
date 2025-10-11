from time import sleep
import shutil
import subprocess
import os
import sys
import ctypes
import tempfile


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
