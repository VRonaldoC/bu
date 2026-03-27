import subprocess
import sys
import os
import platform

# ====== FIX RENDER ======
def safe_exit():
    sys.exit()

try:
    token_number = int(sys.stdin.readline().strip())
except:
    token_number = 1
# =========================

# Listas de servidores
ntp_servers = [
    "ntp0.ntp-servers.net", "ntp1.ntp-servers.net", "ntp2.ntp-servers.net",
    "ntp3.ntp-servers.net", "ntp4.ntp-servers.net", "ntp5.ntp-servers.net",
    "ntp6.ntp-servers.net"
]

MI_SERVERS = ['161.117.96.161', '20.157.18.26']

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ["requests", "ntplib", "pytz", "urllib3", "icmplib", "colorama", "linecache"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install_package(package)

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

init(autoreset=True)

col_g = Fore.GREEN
col_gb = Style.BRIGHT + Fore.GREEN
col_b = Fore.BLUE
col_bb = Style.BRIGHT + Fore.BLUE
col_y = Fore.YELLOW
col_yb = Style.BRIGHT + Fore.YELLOW
col_r = Fore.RED
col_rb = Style.BRIGHT + Fore.RED

scriptversion = "ARU_FHL_v070425"

print(col_yb + f"{scriptversion}_токен_#{token_number}:")
print(col_y + "Verificando estado de la cuenta")

token = linecache.getline("token.txt", token_number).strip()
cookie_value = token

# ===== FIX TIMESHiFT POR TOKEN =====
timeshift_file = f"timeshift_{token_number}.txt"
feedtime = float(linecache.getline(timeshift_file, 1).strip())
feed_time_shift = feedtime
feed_time_shift_1 = feed_time_shift / 1000
# ===================================

def generate_device_id():
    random_data = f"{random.random()}-{time.time()}"
    return hashlib.sha1(random_data.encode('utf-8')).hexdigest().upper()

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

def get_synchronized_beijing_time(start_beijing_time, start_timestamp):
    elapsed = time.time() - start_timestamp
    return start_beijing_time + timedelta(seconds=elapsed)

class HTTP11Session:
    def __init__(self):
        self.http = urllib3.PoolManager(
            maxsize=10,
            retries=True,
            timeout=urllib3.Timeout(connect=2.0, read=15.0),
            headers={}
        )

    def make_request(self, method, url, headers=None, body=None):
        try:
            request_headers = headers or {}
            request_headers['Content-Type'] = 'application/json; charset=utf-8'
            return self.http.request(
                method,
                url,
                headers=request_headers,
                body=body,
                preload_content=False
            )
        except:
            return None

def main():
    device_id = generate_device_id()
    session = HTTP11Session()

    start_beijing_time = get_initial_beijing_time()
    if start_beijing_time is None:
        safe_exit()

    start_timestamp = time.time()

    url = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
    headers = {
        "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
    }

    while True:
        request_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
        print(f"[Solicitud] {request_time}")
        response = session.make_request('POST', url, headers=headers)
        if response:
            try:
                data = json.loads(response.data.decode('utf-8'))
                print(data)
            except:
                pass

if __name__ == "__main__":
    main()
