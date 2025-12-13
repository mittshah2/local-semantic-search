
from PIL import Image
import os

img = Image.open("app_icon.png")
icon_path = "app_icon.ico"
img.save(icon_path, format='ICO', sizes=[(256, 256)])
print(f"Icon saved to {os.path.abspath(icon_path)}")
