def create_lease(asset, price, term):
    return {
        "asset": asset,
        "price": price,
        "term": term,
        "status": "active",
        "message": f"Актив {asset} сдан в лизинг на {term} месяцев за {price} ₸"
    }

def check_gps(asset_id):
    return {"status": "ok", "location": "Павлодар"}

def block_asset(asset_id):
    return {"status": "blocked", "message": "Актив заблокирован"}
