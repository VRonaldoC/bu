import subprocess
import sys
import os
import platform
import hashlib
import linecache
import random
import time
from datetime import datetime, timezone, timedelta
import ntplib
import pytz
import urllib3
import json
from icmplib import ping
from colorama import init, Fore, Style

# -------- CONFIG --------
ntp_servers = [
    "ntp0.ntp-servers.net", "ntp1.ntp-servers.net", "ntp2.ntp-servers.net",
    "ntp3.ntp-servers.net", "ntp4.ntp-servers.net", "ntp5.ntp-servers.net",
    "ntp6.ntp-servers.net"
]

scriptversion = "ARU_FHL_v070425"

# -------- TOKEN DESDE ARGUMENTO --------
token_number = int(sys.argv[1])

# -------- LIMPIAR PANTALLA --------
os.system('cls' if os.name == 'nt' else 'clear')

# -------- COLORES --------
init(autoreset=True)
col_g = Fore.GREEN
col_y = Fore.YELLOW
col_r = Fore.RED

print(f"{scriptversion}_token_#{token_number}")
print("Verificando estado de la cuenta...\n")

# -------- LEER ARCHIVOS --------
token = linecache.getline("token.txt", token_number).strip()
feedtime = float(linecache.getline("timeshift.txt", token_number).strip())
feed_time_shift_1 = feedtime / 1000

# -------- FUNCIONES --------
def generate_device_id():
    random_data = f"{random.random()}-{time.time()}"
    return hashlib.sha1(random_data.encode()).hexdigest().upper()

def get_initial_beijing_time():
    client = ntplib.NTPClient()
    beijing_tz = pytz.timezone("Asia/Shanghai")

    for server in ntp_servers:
        try:
            response = client.request(server, version=3)
            ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
            return ntp_time.astimezone(beijing_tz)
        except:
            continue
    return None

def get_sync_time(start_beijing_time, start_timestamp):
    elapsed = time.time() - start_timestamp
    return start_beijing_time + timedelta(seconds=elapsed)

def wait_until_target(start_beijing_time, start_timestamp):
    next_day = start_beijing_time + timedelta(days=1)
    target = next_day.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=feed_time_shift_1)

    print(f"Esperando hasta {target.strftime('%H:%M:%S.%f')} (UTC+8)")

    while True:
        now = get_sync_time(start_beijing_time, start_timestamp)
        if now >= target:
            break
        time.sleep(0.0005)

# -------- HTTP --------
class HTTP11Session:
    def __init__(self):
        self.http = urllib3.PoolManager()

    def request(self, method, url, headers=None, body=None):
        return self.http.request(method, url, headers=headers, body=body)

# -------- MAIN --------
def main():
    device_id = generate_device_id()
    session = HTTP11Session()

    start_beijing = get_initial_beijing_time()
    if start_beijing is None:
        print("Error NTP")
        return

    start_ts = time.time()
    wait_until_target(start_beijing, start_ts)

    url = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
    headers = {
        "Cookie": f"new_bbs_serviceToken={token};deviceId={device_id};",
        "User-Agent": "okhttp/4.12.0",
        "Content-Type": "application/json"
    }

    while True:
        now = get_sync_time(start_beijing, start_ts)
        print(f"Enviando solicitud a las {now.strftime('%H:%M:%S.%f')}")

        response = session.request("POST", url, headers=headers, body=b'{"is_retry":true}')
        print(response.data.decode())
        time.sleep(0.2)

if __name__ == "__main__":
    main()
