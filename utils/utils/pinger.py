import requests
import time
import threading
import os

def super_pinger():
    url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'zerkalo.onrender.com')}/"
    ping_count = 0
    while True:
        try:
            response = requests.get(url, timeout=10)
            ping_count += 1
            print(f"🔵 Пинг #{ping_count} | Статус: {response.status_code}")
        except:
            pass
        time.sleep(120)

def start_pinger():
    thread = threading.Thread(target=super_pinger, daemon=True)
    thread.start()
