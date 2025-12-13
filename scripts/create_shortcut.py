import os
import sys
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Semantic Search.lnk")
    
    # Paths in the project
    # cwd is now the 'scripts' folder if run from there, or we should resolve relative to file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    venv_python = os.path.join(project_root, "venv", "Scripts", "pythonw.exe")  # Use pythonw.exe to hide console
    target_script = os.path.join(project_root, "main.py")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    
    # Target is Python executable
    shortcut.Targetpath = venv_python
    # Arguments are the script to run
    shortcut.Arguments = f'"{target_script}"'
    # Working directory is the project folder
    shortcut.WorkingDirectory = project_root
    
    # Set Icon
    icon_path = os.path.join(project_root, "resources", "app_icon.ico")
    shortcut.IconLocation = icon_path
    
    shortcut.save()
    print(f"Shortcut created at: {path}")

if __name__ == '__main__':
    create_desktop_shortcut()
