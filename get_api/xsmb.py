import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import config
import json
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

def get_xsmb(date = None):
    url = "https://api.1touch.pro/api/xsmb"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "apikey": API_KEY_1TOUCH
    }
    if date:
        data["ngay"] = date
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        res = response.json()

        ket_qua = res.get("ket_qua", {})
        lines = [f"🎯 Kết quả XSMB ngày {res.get('ngay')}"]

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
        return f"❌ Lỗi khi gọi API: {e}"
    except ValueError:
        return "❌ Phản hồi không phải là JSON hợp lệ."
# Example usage
if __name__ == "__main__":
    result = get_xsmb()
    print(result)