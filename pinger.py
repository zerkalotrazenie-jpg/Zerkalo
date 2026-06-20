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
            print(f"🔵 ПИНГ #{ping_count} | Статус: {response.status_code}")
        except:
            pass
        time.sleep(60)

def start_pinger():
    thread = threading.Thread(target=super_pinger, daemon=True)
    thread.start()
    print("✅ ПИНГ ЗАПУЩЕН")

# Если файл запущен напрямую
if __name__ == "__main__":
    start_pinger()
    while True:
        time.sleep(60)
