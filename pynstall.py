from asyncio import sleep
import subprocess
import os
import sys


def install_chocolatey():
    installationScript = (
        'Set-ExecutionPolicy Bypass -Scope Process -Force; '
        '[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))'
    )
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy",
            "Bypass", "-Command", installationScript],
        check=True
    )


welcome_message = """
===========================================
                pynstall
===========================================
"""

menu = """
1 = Install an app
2 = Create a profile
3 = Run a profile

TIP: To come back to this menu at any time, just type "back".
"""

print(welcome_message, menu)

chooseOption = input("Which option would you like to choose(1/2)?: ")

if chooseOption == "1":

    whichApp = input("Type the name of the app you want to install: ")

    if whichApp.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    print("Installing Chocolatey...")

    sleep(2)

    install_chocolatey()

    print(f"Installing {whichApp}...")

    sleep(2)

    subprocess.run(["choco", "install", whichApp, "-y"], check=True)

if chooseOption == "2":

    profileName = input("Type the name of the profile you want to create: ")

    if profileName.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    with open(f"{profileName}.txt", "w") as profileFile:
        appNames = input(
            "Type the names of the apps you want to add to the profile (separated by commas): ")
        for appName in appNames.split(","):
            profileFile.write(appName.strip() + "\n")

    print(f"Your profile '{profileName}.txt' has been created successfully.")

if chooseOption == "3":
    inputProfileName = input("Type the name of the profile you want to run: ")

    if inputProfileName.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if os.path.exists(f"{inputProfileName}.txt"):
        print(f"Installing apps from profile '{inputProfileName}.txt'...")

        install_chocolatey()

        with open(f"{inputProfileName}.txt", "r") as profileFile:
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
        print(f"Profile '{inputProfileName}.txt' does not exist.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
