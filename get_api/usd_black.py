import re
import requests
from bs4 import BeautifulSoup

URL = "https://tygiausd.org/"


def _extract_number(text):
    if not text:
        return None
    first_token = text.replace("\xa0", " ").strip().split()[0]
    match = re.search(r"(\d[\d.,]*)", first_token)
    if not match:
        return None
    digits = re.sub(r"\D", "", match.group(1))
    if not digits:
        return None
    return int(digits)


def get_usd_black_rate():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "text/html",
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Connection": "keep-alive",
    }

    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    row = soup.select_one("table tr:has(h3)")
    if row is None:
        raise ValueError("Không tìm thấy dòng tỷ giá USD chợ đen")

    tds = row.find_all("td")
    if len(tds) < 2:
        raise ValueError("Dữ liệu tỷ giá USD chợ đen không hợp lệ")

    buy = _extract_number(tds[0].get_text(" ", strip=True))
    sell = _extract_number(tds[1].get_text(" ", strip=True))

    if buy is None or sell is None:
        raise ValueError("Không thể parse giá mua/bán USD chợ đen")

    return {
        "currency": "USD",
        "buy": float(buy),
        "sell": float(sell),
        "source": "Chợ đen"
    }
