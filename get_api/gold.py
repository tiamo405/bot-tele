import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from bs4 import BeautifulSoup
import config

URL_SJC = "https://giavang.org/trong-nuoc/sjc/"
URL_DOJI = "https://giavang.org/trong-nuoc/doji/"
URL_GOLDAPI = config.URL_GOLDAPI

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
        print("Error:", str(e))

def get_gold(url=URL_SJC):
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
    result["gia_usd"] = make_gapi_request()
    # === Thời gian cập nhật ===
    update_time = soup.select_one("h1.box-headline small")
    if update_time:
        result["cap_nhat"] = update_time.text.strip()

    return result



if __name__ == "__main__":
    gold_data = get_gold(URL_DOJI)
    print(gold_data)
