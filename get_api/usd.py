import requests
import xml.etree.ElementTree as ET

def get_vcb_exchange_rate(currency_code):
    url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    root = ET.fromstring(r.content)

    for exrate in root.findall("Exrate"):
        if exrate.attrib["CurrencyCode"] == currency_code.upper():
            buy = exrate.attrib["Buy"]
            sell = exrate.attrib["Sell"]

            # bỏ dấu , để dễ xử lý số
            buy = None if buy == "-" else float(buy.replace(",", ""))
            sell = None if sell == "-" else float(sell.replace(",", ""))

            return {
                "currency": currency_code.upper(),
                "buy": buy,
                "sell": sell,
                "source": "Vietcombank"
            }

    return None
if __name__ == "__main__":
    rate = get_vcb_exchange_rate("USD")
    print(rate)