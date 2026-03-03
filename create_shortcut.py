import os
import sys

# Ensure PIL and pywin32 are available
try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    os.system(sys.executable + " -m pip install Pillow")
    from PIL import Image

try:
    import win32com.client
except ImportError:
    print("Installing pywin32...")
    os.system(sys.executable + " -m pip install pywin32")
    import win32com.client


def create_shortcut_with_icon():
    # Paths
    png_path = r"C:\Users\inwon\.gemini\antigravity\brain\d4da1785-89ea-42e2-8b66-2d1dcde88aca\stylish_news_icon_1772493491457.png"
    workspace_dir = r"C:\workspace\Daily_news\notebooklm-mcp"
    ico_path = os.path.join(workspace_dir, "stylish_app_icon.ico")
    target_bat = os.path.join(workspace_dir, "Run_DailyNews.bat")
    
    # 1. Convert PNG to ICO
    print(f"Converting image to icon...")
    if not os.path.exists(png_path):
        print(f"Error: PNG not found at {png_path}")
        return
        
    img = Image.open(png_path)
    # Save as ICO with multiple sizes for best desktop display
    img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    print(f"Icon saved successfully: {ico_path}")

    # 2. Create Desktop Shortcut
    print(f"Creating shortcut on Desktop...")
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop, "Daily News Automator.lnk")
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_bat
    shortcut.WorkingDirectory = workspace_dir
    shortcut.IconLocation = ico_path
    shortcut.save()
    
    print(f"Shortcut created successfully at: {shortcut_path}")
    print("You can now launch the app directly from your Desktop with the new icon!")

if __name__ == "__main__":
    create_shortcut_with_icon()
