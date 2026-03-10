import os
import sys

# Thêm đường dẫn để tìm file config.py ở thư mục cha
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
try:
    from config import GEMINI_API_KEY
except ImportError:
    print("Lỗi: Không tìm thấy file config.py hoặc GEMINI_API_KEY. Hãy kiểm tra lại vị trí file.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

def ask_ai(question):
    """
    Gửi câu hỏi tới Gemini AI và nhận câu trả lời.
    
    Args:
        question (str): Câu hỏi của người dùng
        
    Returns:
        str: Câu trả lời từ AI hoặc thông báo lỗi
    """
    try:
        # Prompt được thiết kế để câu trả lời CỰC KỲ ngắn gọn
        system_prompt = """Bạn là trợ lý AI. Trả lời CỰC NGẮN GỌN.

QUY TẮC BỮT BUỘC:
1. Trả lời tối đa 1-2 câu (hoặc 3-5 dòng code)
2. Không giải thích dài dòng, CHỈ trả lời trực tiếp
3. Nếu là code: CHỈ code cốt lõi, KHÔNG có ví dụ sử dụng
4. Nếu giải thích: CHỈ 1-2 câu định nghĩa ngắn nhất
5. Trả lời bằng TIẾNG VIỆT
6. KHÔNG có mở đầu kiểu "Chào bạn", "Đây là..."

Trả lời:"""

        full_prompt = f"{system_prompt}\n\n{question}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        
        return response.text
        
    except Exception as e:
        return f"❌ Lỗi khi gọi API: {str(e)}"

# Test code (chỉ chạy khi run trực tiếp file này)
if __name__ == "__main__":
    test_question = "giải thích về trí tuệ nhân tạo"
    print(ask_ai(test_question))