import requests
from bs4 import BeautifulSoup

URL_SJC = "https://giavang.org/trong-nuoc/sjc/"
URL_DOJI = "https://giavang.org/trong-nuoc/doji/"

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

    # === Thời gian cập nhật ===
    update_time = soup.select_one("h1.box-headline small")
    if update_time:
        result["cap_nhat"] = update_time.text.strip()

    return result



if __name__ == "__main__":
    gold_data = get_gold(URL_DOJI)
    print(gold_data)
