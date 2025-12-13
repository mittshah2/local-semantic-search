import os
import sys
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Semantic Search.lnk")
    
    # Paths in the project
    cwd = os.getcwd()
    venv_python = os.path.join(cwd, "venv", "Scripts", "pythonw.exe")  # Use pythonw.exe to hide console
    target_script = os.path.join(cwd, "main.py")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    
    # Target is Python executable
    shortcut.Targetpath = venv_python
    # Arguments are the script to run
    shortcut.Arguments = f'"{target_script}"'
    # Working directory is the project folder
    shortcut.WorkingDirectory = cwd
    
    shortcut.save()
    print(f"Shortcut created at: {path}")

if __name__ == '__main__':
    create_desktop_shortcut()
