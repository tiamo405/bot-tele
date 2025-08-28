import re
import requests
from bs4 import BeautifulSoup
import json

def fetch_lich_xemlicham(url: str):
    """
    Trả về: list[list[dict|None]]
    - Mỗi hàng là 1 tuần; mỗi ô là:
      {
        'duong': int,             # ngày dương
        'am_text': '10/7 Quý Dậu',
        'am_day': '10/7',         # hoặc '21'
        'am_can_chi': 'Quý Dậu',  # có thể None nếu không in
        'good_bad': 'tot'|'xau'|None
      }
      hoặc None nếu là ô trống (class 'skip').
    """
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.select_one('table.vncal')
    if not table:
        return []

    out = []
    for tr in table.select('tbody tr'):
        row = []
        for td in tr.find_all('td'):
            # Ô trống ở cuối tháng
            if 'skip' in (td.get('class') or []):
                row.append(None)
                continue

            a = td.find('a')
            if not a:
                row.append(None)
                continue

            d_duong = a.select_one('.duong')
            d_am = a.select_one('.am')
            flag = a.select_one('.dao')  # có class 'tot' hoặc 'xau'

            item = {
                'duong': int(d_duong.get_text(strip=True)) if d_duong else None,
                'am_text': d_am.get_text(" ", strip=True) if d_am else None,
                'am_day': None,
                'am_can_chi': None,
                'good_bad': (
                    'xau' if (flag and 'xau' in (flag.get('class') or []))
                    else 'tot' if (flag and 'tot' in (flag.get('class') or []))
                    else None
                ),
            }

            # Tách "10/7 Quý Dậu" hoặc "21 Giáp Thân"
            if item['am_text']:
                m = re.match(r'(\d{1,2}(?:/\d{1,2})?)\s*(.*)?', item['am_text'])
                if m:
                    item['am_day'] = m.group(1)
                    item['am_can_chi'] = m.group(2).strip() if m.group(2) else None

            row.append(item)
        out.append(row)
    return out

def solar_to_lunar(day, month, year):
    """
    Chuyển đổi từ lịch dương sang âm lịch
    Args:
        day (int): Ngày dương lịch
        month (int): Tháng dương lịch  
        year (int): Năm dương lịch
    Returns:
        dict: Kết quả chuyển đổi hoặc None nếu lỗi
    """
    try:
        url = "https://open.oapi.vn/date/convert-to-lunar"
        payload = {
            "day": day,
            "month": month, 
            "year": year
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") == "success":
            return data.get("data")
        else:
            return None
            
    except Exception as e:
        print(f"Error converting solar to lunar: {e}")
        return None

def lunar_to_solar(day, month, year):
    """
    Chuyển đổi từ âm lịch sang lịch dương
    Args:
        day (int): Ngày âm lịch
        month (int): Tháng âm lịch
        year (int): Năm âm lịch
    Returns:
        dict: Kết quả chuyển đổi hoặc None nếu lỗi
    """
    try:
        url = "https://open.oapi.vn/date/convert-to-solar"
        payload = {
            "day": day,
            "month": month,
            "year": year
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") == "success":
            return data.get("data")
        else:
            return None
            
    except Exception as e:
        print(f"Error converting lunar to solar: {e}")
        return None

# Ví dụ dùng:
if __name__ == "__main__":
    url = "https://www.xemlicham.com/am-lich/nam/2025/thang/9"
    data = fetch_lich_xemlicham(url)
    # In thử ngày 2/9
    print(data[1])  # Ô thứ Ba tuần 1
