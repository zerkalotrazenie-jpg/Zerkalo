ADMIN_IDS = [5409420822, 5479179814]

def get_role(user_id):
    if user_id in ADMIN_IDS:
        return "Хранитель"
    return "Пользователь"

def has_access(user_id, action):
    role = get_role(user_id)
    if role == "Хранитель":
        return True
    if action in ["view", "chat"]:
        return True
    return False
