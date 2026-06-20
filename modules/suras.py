def load_suras():
    try:
        with open("suras/suras.txt", "r", encoding="utf-8") as f:
            content = f.read()
        raw_suras = content.split("СУРА ")[1:]
        suras = []
        for raw in raw_suras:
            lines = raw.strip().split("\n")
            if lines:
                suras.append({
                    "number": lines[0].strip(),
                    "text": "\n".join(lines[1:])
                })
        return suras
    except FileNotFoundError:
        return []

SURAS = load_suras()
print(f"✅ Загружено {len(SURAS)} сур")

def get_sura_by_number(num):
    for s in SURAS:
        if s["number"] == str(num):
            return s
    return None

def get_all_suras():
    return SURAS
