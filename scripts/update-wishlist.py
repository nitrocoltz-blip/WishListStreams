import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

STEAM_ID = "76561199122871618"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "wishlist.json"
MANUAL = ROOT / "data" / "manual.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/136 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
}


def get_json(url, retries=3):
    last = None
    for intento in range(retries):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception as error:
            last = error
            time.sleep(2 * (intento + 1))
    raise last


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def get_wishlist():
    url = "https://api.steampowered.com/IWishlistService/GetWishlist/v1/?" + urllib.parse.urlencode({"steamid": STEAM_ID})
    items = get_json(url).get("response", {}).get("items", [])
    if not items:
        raise RuntimeError("Steam no ha devuelto elementos: revisa que el perfil y los detalles de juego sean públicos.")
    return items


def get_details(appid):
    url = "https://store.steampowered.com/api/appdetails/?" + urllib.parse.urlencode({"appids": appid, "cc": "es", "l": "spanish"})
    try:
        entry = get_json(url, retries=2).get(str(appid), {})
        if entry.get("success"):
            return entry.get("data", {})
    except Exception:
        pass
    return {}


def get_price(details):
    if details.get("is_free"):
        return "Gratis"
    return (details.get("price_overview") or {}).get("final_formatted", "")


def main():
    anteriores = {int(i["appid"]): i for i in read_json(OUTPUT, {}).get("items", [])}
    manual = {k: v for k, v in read_json(MANUAL, {}).items() if not k.startswith("_")}
    wishlist = get_wishlist()
    # En Steam, priority 0 significa "sin clasificar": va al final.
    wishlist.sort(key=lambda i: (int(i.get("priority", 0)) or 10**9, int(i.get("date_added", 0))))

    items, vistos = [], set()
    for posicion, item in enumerate(wishlist, 1):
        appid = int(item.get("appid", 0))
        if not appid:
            continue
        vistos.add(appid)
        previo = anteriores.get(appid, {})
        details = get_details(appid)
        entrada = {
            "appid": appid,
            # Si Steam no responde con los detalles, se conserva lo que ya había.
            "name": details.get("name") or previo.get("name") or f"Juego {appid}",
            "price": get_price(details) if details else previo.get("price", ""),
            "priority": posicion,
            "date_added": int(item.get("date_added", 0)),
            "capsule": details.get("header_image") or previo.get("capsule")
                       or f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg",
            "type": details.get("type") or previo.get("type", "game"),
        }
        entrada.update({k: v for k, v in manual.get(str(appid), {}).items() if k in ("gifted", "giftedBy", "note")})
        items.append(entrada)
        time.sleep(0.2)

    # Cuando te regalan un juego, Steam lo quita de la wishlist. Si lo marcas
    # como gifted en manual.json, se mantiene en la página como "Regalado".
    for clave, datos in manual.items():
        appid = int(clave)
        if appid not in vistos and datos.get("gifted") and appid in anteriores:
            entrada = dict(anteriores[appid])
            entrada.update({k: v for k, v in datos.items() if k in ("gifted", "giftedBy", "note")})
            entrada["priority"] = len(items) + 1
            items.append(entrada)

    OUTPUT.write_text(
        json.dumps({"updatedAt": int(time.time() * 1000), "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK: {len(items)} juegos")


if __name__ == "__main__":
    main()
