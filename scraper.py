import requests
import json
import re
from datetime import datetime

TIRES = [
    {"id": 1,  "brand": "Michelin",    "model": "Pilot Sport 4",      "size": "225/45R18"},
    {"id": 2,  "brand": "Bridgestone", "model": "Turanza T005A",       "size": "205/55R16"},
    {"id": 3,  "brand": "Continental", "model": "ComfortContact CC6",  "size": "215/55R17"},
    {"id": 4,  "brand": "Yokohama",    "model": "BluEarth-A AE50",     "size": "205/55R16"},
    {"id": 5,  "brand": "Pirelli",     "model": "P Zero",              "size": "245/40R19"},
    {"id": 6,  "brand": "Michelin",    "model": "Energy Saver+",       "size": "195/65R15"},
    {"id": 7,  "brand": "Bridgestone", "model": "Ecopia EP300",        "size": "185/65R15"},
    {"id": 8,  "brand": "Toyo",        "model": "Proxes CF2",          "size": "205/55R16"},
    {"id": 9,  "brand": "Yokohama",    "model": "ADVAN Fleva V701",    "size": "215/55R17"},
    {"id": 10, "brand": "Continental", "model": "PremiumContact 6",    "size": "225/45R18"},
    {"id": 11, "brand": "Dunlop",      "model": "SP Sport Maxx RT2",   "size": "225/45R17"},
    {"id": 12, "brand": "Pirelli",     "model": "Cinturato P7",        "size": "205/55R16"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def fetch_pchome(brand, model, size):
    query = f"{brand} {model} {size}"
    try:
        url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={requests.utils.quote(query)}&page=1&sort=rnk/dc"
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        prods = r.json().get("prods", [])
        prices = [p["price"] for p in prods if isinstance(p.get("price"), (int, float)) and p["price"] > 0]
        if prices:
            result = int(min(prices))
            print(f"    PChome ✅ NT${result:,}")
            return result
    except Exception as e:
        print(f"    PChome ❌ {e}")
    return None

def fetch_shopee(brand, model, size):
    query = f"{brand} {model} {size}"
    try:
        url = f"https://shopee.tw/api/v4/search/search_items?by=relevancy&keyword={requests.utils.quote(query)}&limit=20&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
        headers = {**HEADERS, "referer": "https://shopee.tw/", "x-api-source": "pc"}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        items = r.json().get("items", [])
        prices = []
        for item in items:
            p = item.get("item_basic", {}).get("price")
            if p and p > 0:
                prices.append(int(p) // 100000)
        if prices:
            result = min(prices)
            print(f"    蝦皮   ✅ NT${result:,}")
            return result
    except Exception as e:
        print(f"    蝦皮   ❌ {e}")
    return None

def fetch_yahoo(brand, model, size):
    query = f"{brand} {model} {size}"
    try:
        url = f"https://tw.buy.yahoo.com/search/product?p={requests.utils.quote(query)}&sort=price"
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        prices_raw = re.findall(r'"price"\s*:\s*(\d+)', r.text)
        prices_raw += re.findall(r'data-price="(\d+)"', r.text)
        prices = [int(p) for p in prices_raw if 500 < int(p) < 100000]
        if prices:
            result = min(prices)
            print(f"    Yahoo  ✅ NT${result:,}")
            return result
    except Exception as e:
        print(f"    Yahoo  ❌ {e}")
    return None

def fetch_ruten(brand, model, size):
    query = f"{brand} {model} {size}"
    try:
        url = f"https://find.ruten.com.tw/s/v2/search.php?q={requests.utils.quote(query)}&sort=prc/asc&g=0"
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        prices_raw = re.findall(r'"price"\s*:\s*(\d+(?:\.\d+)?)', r.text)
        prices = [int(float(p)) for p in prices_raw if 500 < float(p) < 100000]
        if prices:
            result = min(prices)
            print(f"    露天   ✅ NT${result:,}")
            return result
    except Exception as e:
        print(f"    露天   ❌ {e}")
    return None

def fetch_leetire(brand, model, size):
    query = f"{brand} {model} {size}"
    try:
        url = f"https://www.lee-tire.com.tw/tyre?keyword={requests.utils.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        prices_raw = re.findall(r'(?:NT\$|＄|\$)\s*([\d,]+)', r.text)
        prices = [int(p.replace(',', '')) for p in prices_raw if 500 < int(p.replace(',', '')) < 100000]
        if prices:
            result = min(prices)
            print(f"    小李   ✅ NT${result:,}")
            return result
    except Exception as e:
        print(f"    小李   ❌ {e}")
    return None

def fetch_ttshop(brand, model, size):
    query = f"{brand} {model} {size}"
    try:
        url = f"https://www.ttshop.com.tw/product.php?_path=product_search&keyword={requests.utils.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        prices_raw = re.findall(r'(?:NT\$|＄|\$)\s*([\d,]+)', r.text)
        prices = [int(p.replace(',', '')) for p in prices_raw if 500 < int(p.replace(',', '')) < 100000]
        if prices:
            result = min(prices)
            print(f"    台中館 ✅ NT${result:,}")
            return result
    except Exception as e:
        print(f"    台中館 ❌ {e}")
    return None

def main():
    print("=" * 50)
    print(f"🚀 開始抓取 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    results = []
    for tire in TIRES:
        b, m, s = tire["brand"], tire["model"], tire["size"]
        print(f"\n🔍 {b} {m} ({s})")
        row = {
            "id":    tire["id"],
            "brand": b,
            "model": m,
            "size":  s,
            "prices": {
                "pchome":  fetch_pchome(b, m, s),
                "shopee":  fetch_shopee(b, m, s),
                "yahoo":   fetch_yahoo(b, m, s),
                "ruten":   fetch_ruten(b, m, s),
                "leetire": fetch_leetire(b, m, s),
                "ttshop":  fetch_ttshop(b, m, s),
            },
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        valid = [v for v in row["prices"].values() if v is not None]
        if valid:
            print(f"  💰 最低價：NT${min(valid):,}")
        results.append(row)

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "tires": results
        }, f, ensure_ascii=False, indent=2)

    print("\n✅ prices.json 已儲存！")

if __name__ == "__main__":
    main()
