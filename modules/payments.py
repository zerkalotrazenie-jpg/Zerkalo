import os
import time
import hashlib
import random
import requests

TRUST_WALLET_ADDRESS = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY")
KASPI_CLONE_API_KEY = os.environ.get("KASPI_CLONE_API_KEY")

def generate_qr(amount, description="Оплата через Зеркало"):
    return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=Оплата%20{amount}%20тг%20{description}"

def get_trust_balance():
    try:
        url = f"https://api.trongrid.io/v1/accounts/{TRUST_WALLET_ADDRESS}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get("balance", 0) / 1_000_000
    except:
        return 0

def convert_usdt_to_kzt(amount_usdt):
    return int(amount_usdt * 500)

def calculate_commission(amount, rate=0.10):
    return int(amount * rate)

def generate_transaction_id():
    return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

def get_price_for_service(service_type):
    prices = {
        "contact": 1000,
        "subscription": 5000,
        "advertising": 10000,
        "leasing": 50000,
        "automation": 90000,
        "order": 1000,
    }
    return prices.get(service_type, 1000)
