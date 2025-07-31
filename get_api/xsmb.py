import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import config
from bs4 import BeautifulSoup
from datetime import datetime
import re
API_KEY_1TOUCH = config.API_KEY_1TOUCH


# curl -X POST -H "Content-Type: application/json" -d '{
#   "apikey": "abc123xyz",
#   "ngay": "21-04-2025"
# }' https://api.1touch.pro/api/xsmb
# reponse
# {
#   "ngay": "21-04-2025",
#   "tinh": "Miền Bắc",
#   "ma": "MB",
#   "ket_qua": {
#     "giaidb": ["123456"],
#     "giai1": ["23456"],
#     "giai2": ["12345", "67890"],
#     "giai3": ["11111", "22222", "33333"]
#   }
# }

# def get_xsmb(date = None):
#     url = "https://api.1touch.pro/api/xsmb"
#     headers = {
#         "Content-Type": "application/json"
#     }
#     data = {
#         "apikey": API_KEY_1TOUCH
#     }
#     if date:
#         data["ngay"] = date
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
#         res = response.json()

#         ket_qua = res.get("ket_qua", {})
#         lines = [f"🎯 Kết quả XSMB ngày {res.get('ngay')}"]

#         if "giaidb" in ket_qua:
#             lines.append(f"🏆 Giải ĐB: {', '.join(ket_qua['giaidb'])}")
#         if "giai1" in ket_qua:
#             lines.append(f"🥇 Giải 1: {', '.join(ket_qua['giai1'])}")
#         if "giai2" in ket_qua:
#             lines.append(f"🥈 Giải 2: {', '.join(ket_qua['giai2'])}")
#         if "giai3" in ket_qua:
#             lines.append(f"🥉 Giải 3: {', '.join(ket_qua['giai3'])}")
#         if "giai4" in ket_qua:
#             lines.append(f"🎖 Giải 4: {', '.join(ket_qua['giai4'])}")
#         if "giai5" in ket_qua:
#             lines.append(f"🏅 Giải 5: {', '.join(ket_qua['giai5'])}")
#         if "giai6" in ket_qua:
#             lines.append(f"🎗 Giải 6: {', '.join(ket_qua['giai6'])}")
#         if "giai7" in ket_qua:
#             lines.append(f"🎫 Giải 7: {', '.join(ket_qua['giai7'])}")

#         return "\n".join(lines)

#     except requests.RequestException as e:
#         return f"❌ Lỗi khi gọi API: {e}"
#     except ValueError:
#         return "❌ Phản hồi không phải là JSON hợp lệ."
# # Example usage
# if __name__ == "__main__":
#     result = get_xsmb()
#     print(result)

def format_date(date_str):
    """
    Chuyển đổi format ngày từ 01-07-2025 thành 1-7-2025
    Bỏ số 0 đầu của ngày và tháng
    """
    if not date_str:
        return date_str
    
    parts = date_str.split('-')
    if len(parts) == 3:
        day = str(int(parts[0]))    # Bỏ số 0 đầu của ngày
        month = str(int(parts[1]))  # Bỏ số 0 đầu của tháng
        year = parts[2]
        return f"{day}-{month}-{year}"
    
    return date_str


def get_xsmb(ngay=None):
    """
    Trích xuất kết quả XSMB từ website xsmn.mobi
    
    Args:
        ngay (str, optional): Ngày cần lấy kết quả theo format "dd-mm-yyyy". 
                             Nếu None thì lấy kết quả hôm nay.
    
    Returns:
        str: Chuỗi kết quả XSMB đã format
    """
    try:
        # Nếu không có ngày, lấy ngày hiện tại
        ngay = format_date(ngay)
        
        # Format URL
        url = f"https://xsmn.mobi/xsmb-{ngay.replace('-', '-')}.html"
        
        # Gửi request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm bảng kết quả
        table = soup.find('table', class_='extendable kqmb colgiai read-result')
        if not table:
            return f"❌ Không tìm thấy kết quả XSMB cho ngày {ngay}"
        
        # Khởi tạo dict kết quả
        ket_qua = {}
        
        # Trích xuất từng giải
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                giai_text = cells[0].get_text(strip=True)
                so_text = cells[1].get_text(strip=True)
                
                # Trích xuất số từ các span
                numbers = []
                spans = cells[1].find_all('span')
                if spans:
                    for span in spans:
                        num = span.get_text(strip=True)
                        if num and num.isdigit():
                            numbers.append(num)
                else:
                    # Fallback: tách số từ text
                    nums = re.findall(r'\d+', so_text)
                    numbers = [num for num in nums if len(num) >= 2]
                
                # Map tên giải
                if giai_text == "ĐB":
                    ket_qua["giaidb"] = numbers
                elif giai_text == "G.1":
                    ket_qua["giai1"] = numbers
                elif giai_text == "G.2":
                    ket_qua["giai2"] = numbers
                elif giai_text == "G.3":
                    ket_qua["giai3"] = numbers
                elif giai_text == "G.4":
                    ket_qua["giai4"] = numbers
                elif giai_text == "G.5":
                    ket_qua["giai5"] = numbers
                elif giai_text == "G.6":
                    ket_qua["giai6"] = numbers
                elif giai_text == "G.7":
                    ket_qua["giai7"] = numbers
        
        # Format kết quả theo yêu cầu
        lines = [f"🎯 Kết quả XSMB ngày {ngay}"]
        
        if "giaidb" in ket_qua:
            lines.append(f"🏆 Giải ĐB: {', '.join(ket_qua['giaidb'])}")
        if "giai1" in ket_qua:
            lines.append(f"🥇 Giải 1: {', '.join(ket_qua['giai1'])}")
        if "giai2" in ket_qua:
            lines.append(f"🥈 Giải 2: {', '.join(ket_qua['giai2'])}")
        if "giai3" in ket_qua:
            lines.append(f"🥉 Giải 3: {', '.join(ket_qua['giai3'])}")
        if "giai4" in ket_qua:
            lines.append(f"🎖 Giải 4: {', '.join(ket_qua['giai4'])}")
        if "giai5" in ket_qua:
            lines.append(f"🏅 Giải 5: {', '.join(ket_qua['giai5'])}")
        if "giai6" in ket_qua:
            lines.append(f"🎗 Giải 6: {', '.join(ket_qua['giai6'])}")
        if "giai7" in ket_qua:
            lines.append(f"🎫 Giải 7: {', '.join(ket_qua['giai7'])}")
        
        return "\n".join(lines)
        
    except requests.RequestException as e:
        return f"❌ Lỗi khi gọi API: {e}, cấu trúc gọi hàm /xsmb hoặc /xsmb dd-mm-yyyy (/xsmb 29-07-2025)"
    except ValueError:
        return "❌ Phản hồi không phải là JSON hợp lệ."
    except Exception as e:
        return f"❌ Lỗi không xác định: {e}"

# Hàm phụ trợ để test
def test_get_xsmb():
    """Test hàm get_xsmb với ngày 29-7-2025"""
    result = get_xsmb("30-7-2025")
    print(result)

# Chạy test
if __name__ == "__main__":
    test_get_xsmb()