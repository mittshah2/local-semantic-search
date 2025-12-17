import webview
import os
import threading
from search_engine import SearchEngine

class Api:
    def __init__(self):
        self.engine = SearchEngine()

    def search(self, query):
        print(f"Searching for: {query}")
        return self.engine.search(query)
    
    def get_status(self):
        return self.engine.get_status()

    def open_file(self, path):
        print(f"Opening: {path}")
        if os.path.exists(path):
            os.startfile(path)
        else:
            print("File not found.")

import ctypes
from settings import APP_ID

def main():
    # Set AppUserModelID to group window with shortcut
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception as e:
        print(f"Failed to set AppUserModelID: {e}")

    api = Api()
    
    # Get absolute path to index.html
    gui_dir = os.path.join(os.path.dirname(__file__), 'gui')
    index_path = os.path.join(gui_dir, 'index.html')
    
    window = webview.create_window(
        'Semantic File Search', 
        url=index_path,
        js_api=api,
        width=1000,
        height=700,
        background_color='#050505'
    )
    
    webview.start(debug=False)

if __name__ == '__main__':
    main()
