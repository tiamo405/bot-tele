# AI Handler - Tài liệu hướng dẫn

## Tổng quan

Tính năng `/ai` cho phép người dùng hỏi đáp với Gemini AI (Google) trực tiếp qua Telegram bot. AI được tối ưu để trả lời ngắn gọn, súc tích với code syntax đẹp.

## Cài đặt

### 1. Cài đặt package

```bash
pip install google-genai
```

Package đã được thêm vào `requirements.txt`.

### 2. Cấu hình API Key

Thêm vào file `.env`:

```bash
GEMINI_API_KEY="your_api_key_here"
```

Lấy API key miễn phí tại: https://ai.google.dev/gemini-api/docs/api-key

### 3. Files đã tạo/sửa đổi

- ✅ `get_api/ai.py` - API wrapper cho Gemini
- ✅ `handlers/ai.py` - Telegram handler cho command /ai
- ✅ `config.py` - Thêm GEMINI_API_KEY
- ✅ `app.py` - Import và đăng ký AI handler  
- ✅ `handlers/help.py` - Thêm hướng dẫn /ai
- ✅ `requirements.txt` - Thêm google-genai
- ✅ `test_ai.py` - Test script

## Sử dụng

### Cú pháp

```
/ai <câu hỏi của bạn>
```

### Ví dụ

1. **Giải thích khái niệm:**
   ```
   /ai Giải thích về blockchain
   ```

2. **Viết code:**
   ```
   /ai Viết code Python tính số fibonacci
   ```

3. **So sánh công nghệ:**
   ```
   /ai Sự khác biệt giữa React và Vue.js
   ```

4. **Hỏi về lập trình:**
   ```
   /ai Cách sử dụng async/await trong JavaScript
   ```

5. **Dịch thuật:**
   ```
   /ai Dịch sang tiếng Anh: Xin chào, bạn khỏe không?
   ```

## Đặc điểm

### Prompt Engineering

AI được cấu hình với system prompt tối ưu:

- ✅ Trả lời ngắn gọn (tối đa 500 từ)
- ✅ Đi thẳng vào vấn đề
- ✅ Code sử dụng Markdown syntax (```python, ```javascript...)
- ✅ Ưu tiên bullet points và numbered lists
- ✅ Có ví dụ thực tế
- ✅ Trả lời bằng tiếng Việt (trừ khi yêu cầu khác)
- ✅ Code có comments ngắn gọn

### Model

- **Model:** `gemini-2.5-flash`
- **Provider:** Google AI
- **Đặc điểm:** Nhanh, chính xác, hỗ trợ tiếng Việt tốt

### Xử lý lỗi

- ❌ Nếu không có câu hỏi → Hiển thị hướng dẫn
- ❌ Nếu API lỗi → Hiển thị thông báo lỗi rõ ràng
- ✅ Response dài > 4096 ký tự → Tự động chia nhỏ

### Logging

Tất cả các request được log vào:
- `bot-logs/ai.log` - Application log
- User action được log qua `log_helper`

## Testing

Chạy test script:

```bash
python test_ai.py
```

Test bao gồm:
1. Câu hỏi giải thích khái niệm
2. Viết code Python
3. So sánh công nghệ

## API Reference

### `get_api/ai.py`

```python
def ask_ai(question: str) -> str:
    """
    Gửi câu hỏi tới Gemini AI và nhận câu trả lời.
    
    Args:
        question: Câu hỏi của người dùng
        
    Returns:
        Câu trả lời từ AI hoặc thông báo lỗi
    """
```

### `handlers/ai.py`

```python
@bot.message_handler(commands=['ai'])
def handle_ai(message):
    """
    Handler cho command /ai
    
    Features:
    - Validate input
    - Send typing indicator
    - Call AI API
    - Handle long responses (>4096 chars)
    - Error handling
    - Logging
    """
```

## Giới hạn

- **Message length:** Telegram giới hạn 4096 ký tự/message (đã xử lý tự động)
- **Rate limit:** Tùy thuộc vào Google AI quota (miễn phí: 15 RPM)
- **Response time:** 2-10 giây tùy độ phức tạp câu hỏi

## Troubleshooting

### Lỗi "No API key was provided"

**Nguyên nhân:** Chưa cấu hình GEMINI_API_KEY trong `.env`

**Giải pháp:**
1. Tạo API key tại https://ai.google.dev/gemini-api/docs/api-key
2. Thêm vào `.env`: `GEMINI_API_KEY="your_key_here"`
3. Restart bot

### Lỗi "404 NOT_FOUND"

**Nguyên nhân:** Model name không tồn tại

**Giải pháp:** Sử dụng model hợp lệ: `gemini-2.5-flash`, `gemini-2.0-flash`, hoặc `gemini-flash-latest`

### Response quá dài bị cắt

**Nguyên nhân:** Telegram giới hạn 4096 ký tự

**Giải pháp:** Đã tự động xử lý - response sẽ được chia thành nhiều messages

## Best Practices

1. **Câu hỏi rõ ràng:** Hỏi cụ thể để nhận câu trả lời chính xác
2. **Ngắn gọn:** Tránh câu hỏi quá dài
3. **Ngữ cảnh:** Cung cấp đủ context nếu cần
4. **Theo dõi:** Check logs để debug nếu có vấn đề

## Ví dụ Output

**Input:**
```
/ai Viết code Python tính factorial
```

**Output:**
````markdown
Chào bạn, đây là code Python để tính giai thừa (factorial):

```python
def factorial(n):
    """
    Tính giai thừa của n (n!).
    
    Args:
        n (int): Số nguyên không âm
        
    Returns:
        int: Giai thừa của n
    """
    if n < 0:
        raise ValueError("n phải là số nguyên không âm")
    elif n == 0 or n == 1:
        return 1
    else:
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

# Ví dụ sử dụng
print(f"5! = {factorial(5)}")  # Kết quả: 120
```
````

## License

Sử dụng Gemini API tuân theo [Google AI Terms of Service](https://ai.google.dev/gemini-api/terms)

## Support

- GitHub Issues: [Link to your repo]
- Developer: [Your name/contact]

---

**Last updated:** March 6, 2026
**Version:** 1.0.0
