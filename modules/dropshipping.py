def connect_seller_buyer(seller, buyer, product, price):
    return {
        "seller": seller,
        "buyer": buyer,
        "product": product,
        "price": price,
        "commission": int(price * 0.10),
        "status": "connected"
    }
