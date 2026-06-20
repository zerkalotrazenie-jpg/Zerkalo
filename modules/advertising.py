def show_ad(product, audience, budget):
    return {
        "product": product,
        "audience": audience,
        "budget": budget,
        "status": "active"
    }

def calculate_ad_commission(budget, rate=0.15):
    return int(budget * rate)
