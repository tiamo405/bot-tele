import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from bs4 import BeautifulSoup
import config

URL_SJC = config.URL_SJC
URL_DOJI = config.URL_DOJI
URL_GOLDAPI = config.URL_GOLDAPI
URL_GOLDAPI_ALPHAVANTAGE = config.URL_GOLDAPI_ALPHAVANTAGE
API_KEY_ALPHAVANTAGE = config.API_KEY_ALPHAVANTAGE

def make_gapi_request():
    api_key = "goldapi-1km4rsmla7qzgk-io"
    symbol = "XAU"
    curr = "USD"
    date = ""

    url = f"{URL_GOLDAPI}/{symbol}/{curr}{date}"
    
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        return result['price']
    except requests.exceptions.RequestException as e:
        # Don't print error, just return None
        return None

def make_alpha_request():
    url = f"{URL_GOLDAPI_ALPHAVANTAGE}?function=GOLD_SILVER_SPOT&symbol=GOLD&apikey={API_KEY_ALPHAVANTAGE}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        result = response.json()
        price = result["price"]
        return price
    except requests.exceptions.RequestException as e:
        # Don't print error, just return None
        return None

def make_gold_XAUUSD_request():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    res = requests.get(URL_DOJI, headers=headers, timeout=10)
    res.raise_for_status()
    data = res.json()
    if not data.get('success'):
        raise Exception("API returned success=false")
    prices = data.get('prices', {})
    if 'XAUUSD' in prices:
        xauusd = prices['XAUUSD']
        return xauusd['buy']  # Convert from USD/oz to USD/gram
    return None

def get_gold_doji():
    """Get DOJI gold price from vang.today JSON API"""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    res = requests.get(URL_DOJI, headers=headers, timeout=3)
    res.raise_for_status()

    # Parse JSON response
    data = res.json()
    
    if not data.get('success'):
        raise Exception("API returned success=false")
    
    prices = data.get('prices', {})
    
    result = {}
    
    # Vàng miếng SJC của DOJI (DOHNL - DOJI Hanoi)
    if 'DOHNL' in prices:
        dohnl = prices['DOHNL']
        result["vang_mieng"] = {
            "mua": f"{dohnl['buy'] / 1000:,.0f} x1000đ/lượng",
            "ban": f"{dohnl['sell'] / 1000:,.0f} x1000đ/lượng"
        }
    
    # Vàng nhẫn DOJI (DOJINHTV - DOJI Jewelry)
    if 'DOJINHTV' in prices:
        dojinhtv = prices['DOJINHTV']
        result["vang_nhan"] = {
            "mua": f"{dojinhtv['buy'] / 1000:,.0f} x1000đ/lượng",
            "ban": f"{dojinhtv['sell'] / 1000:,.0f} x1000đ/lượng"
        }
    
    # Thời gian cập nhật
    if 'time' in data and 'date' in data:
        result["cap_nhat"] = f"{data['time']} {data['date']}"
    
    return result

def get_gold(url=URL_SJC):
    """Get gold price - handles both SJC (HTML scraping) and DOJI (JSON API)"""
    # If DOJI URL, use the JSON API method
    if url == URL_DOJI:
        return get_gold_doji()
    
    # Otherwise use the original HTML scraping method (for SJC)
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    result = {}

    # === Giá vàng MIẾNG ===
    gold_boxes = soup.select(".gold-price-box .box-cgre, .gold-price-box .box-cred")

    # thứ tự trên web: mua -> bán (miếng) rồi mua -> bán (nhẫn)
    result["vang_mieng"] = {
        "mua": gold_boxes[0].select_one(".gold-price").text.strip(),
        "ban": gold_boxes[1].select_one(".gold-price").text.strip()
    }

    result["vang_nhan"] = {
        "mua": gold_boxes[2].select_one(".gold-price").text.strip(),
        "ban": gold_boxes[3].select_one(".gold-price").text.strip()
    }
    # === Thời gian cập nhật ===
    update_time = soup.select_one("h1.box-headline small")
    if update_time:
        result["cap_nhat"] = update_time.text.strip()

    return result



if __name__ == "__main__":
    print("=== Testing DOJI ===")
    gold_doji = get_gold(URL_DOJI)
    print(f"Vàng miếng: Mua {gold_doji['vang_mieng']['mua']} - Bán {gold_doji['vang_mieng']['ban']}")
    print(f"Vàng nhẫn (NHẪN TRÒN 9999 HƯNG THỊNH VƯỢNG): Mua {gold_doji['vang_nhan']['mua']} - Bán {gold_doji['vang_nhan']['ban']}")
    print(f"Cập nhật: {gold_doji.get('cap_nhat', 'N/A')}")
    print("\n=== Testing SJC ===")
    gold_sjc = get_gold(URL_SJC)
    print(f"Vàng miếng: Mua {gold_sjc['vang_mieng']['mua']} - Bán {gold_sjc['vang_mieng']['ban']}")
    print(f"Vàng nhẫn: Mua {gold_sjc['vang_nhan']['mua']} - Bán {gold_sjc['vang_nhan']['ban']}")
    print(f"Cập nhật: {gold_sjc.get('cap_nhat', 'N/A')}")

    # Test GoldAPI
    print("\n=== Testing GoldAPI ===")
    price_usd = make_gold_XAUUSD_request() if make_gold_XAUUSD_request() else make_gapi_request() or make_alpha_request()
    if price_usd:
        print(f"Giá vàng thế giới (USD/oz): {price_usd}")
    else:
        print("Không thể lấy giá vàng thế giới từ cả GoldAPI và Alpha Vantage.")
