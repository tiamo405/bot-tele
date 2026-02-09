import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import config

URL_ANCARAT = config.URL_ANCARAT
URL_GOLDAPI = config.URL_GOLDAPI

def make_gapi_request():
    api_key = "goldapi-1km4rsmla7qzgk-io"
    symbol = "XAG"
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

def gia_bac_ancarat():
    try:
        response = requests.get(URL_ANCARAT)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        res  = {}
        res["name"] = data[1][0]
        res["price"] = data[1][1]
        return res
    except requests.exceptions.RequestException as e:
        print("Error fetching Ancarat silver price:", str(e))
    return "N/A"

def get_silver(url = URL_ANCARAT):
    result = {}
    price_usd_agu = make_gapi_request()
    ancarat = gia_bac_ancarat()

    result["price_usd_agu"] = price_usd_agu
    result["name_ancarat"] = ancarat["name"]
    result["price_ancarat"] = ancarat["price"]
    return result

if __name__ == "__main__":
    price_usd_agu = make_gapi_request()
    print("Current Silver Price (USD/oz):", price_usd_agu)
    ancarat = gia_bac_ancarat()
    print("Giá bạc Ancarat (VND):", ancarat["price"])