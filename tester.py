from asyncio import sleep
import subprocess

def install_chocolatey():
    installationScript = (
        'Set-ExecutionPolicy Bypass -Scope Process -Force; '
        '[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))'
    )
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", installationScript],
        check=True
    )

welcome_message = """
===========================================
                pynstall
===========================================
"""

print(welcome_message)

whichApp = input("Type the name of the app you want to install: ")

print("Installing Chocolatey...")

sleep(2)

install_chocolatey()

print(f"Installing {whichApp}...")

sleep(2)

subprocess.run(["choco", "install", whichApp, "-y"], check=True)