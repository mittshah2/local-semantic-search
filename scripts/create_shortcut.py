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
    
    # Import APP_ID from settings
    sys.path.append(project_root)
    try:
        from settings import APP_ID
    except ImportError:
        print("Could not import settings. Defaulting APP_ID.")
        APP_ID = 'mittshah.localsemanticsearch.gui.1.0'

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

    # Set AppUserModelID on the shortcut
    try:
        from win32com.shell import shell, shellcon
        from win32com.propsys import propsys, pscon
        
        def set_app_user_model_id(link_path, app_id):
            # Get the Property Store for the link
            store = propsys.SHGetPropertyStoreFromParsingName(
                link_path, 
                None, 
                shellcon.GPS_READWRITE, 
                propsys.IID_IPropertyStore
            )
            # define the Property Key for System.AppUserModel.ID
            # System.AppUserModel.ID PKEY: {9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}, 5
            key = propsys.PSGetPropertyKeyFromName("System.AppUserModel.ID")
            
            # Create a PropVariant (pywin32 handles the wrapping usually, or we pass the value directly depending on version)
            # In recent pywin32, passing the string directly often works for SetValue with a PropVariant helper under the hood
            # but using PROPVARIANTType is safer if available.
            pv = propsys.PROPVARIANTType(app_id)
            
            store.SetValue(key, pv)
            store.Commit()
            
        set_app_user_model_id(path, APP_ID)
        print(f"AppUserModelID set to '{APP_ID}'")
        
    except ImportError:
        print("Could not import win32com.shell/propsys. Make sure pywin32 is installed to set AppUserModelID.")
    except Exception as e:
        print(f"Error setting AppUserModelID: {e}")

if __name__ == '__main__':
    create_desktop_shortcut()
