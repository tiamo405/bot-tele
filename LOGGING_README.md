# 📊 Hệ Thống Logging Bot Telegram

## 📝 Tổng Quan
Hệ thống logging đã được cấu hình để ghi lại mọi hoạt động của người dùng khi tương tác với bot, bao gồm cả action thành công và lỗi.

## 📂 Cấu Trúc File Log

### File log chính:
- **`logs/bot_usage.log`** - File log chung cho tất cả các hoạt động của bot (ghi user actions)

### File log riêng cho từng chức năng (ghi chi tiết + lỗi):
- **`logs/stock.log`** - Ghi log chi tiết cho chức năng chứng khoán (xem giá, thêm/xóa mã, thông báo)
- **`logs/tuvi.log`** - Ghi log chi tiết cho chức năng tử vi/horoscope (zodiac sign, day)
- **`logs/lunar.log`** - Ghi log chi tiết cho chức năng lịch âm (conversions)
- **`logs/taixiu.log`** - Ghi log chi tiết cho game tài xỉu (bets, results, wins/losses, stats)
- **`logs/aug.log`** - Ghi log chi tiết cho chức năng giá vàng (manual + scheduled)

## 🔄 Cơ Chế Logging Kép

### 1. Log Chung (bot_usage.log) ✅
Ghi **mọi user action** qua `log_user_action()`:
- User ID, Username, Full Name
- Chat ID, Chat Type
- Command/Action
- Basic details

### 2. Log Riêng (stock.log, aug.log, etc.) 🎯
Ghi **chi tiết cụ thể** cho từng chức năng:
- **Thành công**: Thông tin chi tiết về action
- **Lỗi**: Error messages và stack traces

## 📊 Thông Tin Được Ghi Log

### Log Chung (bot_usage.log):
1. **Timestamp** - Thời gian thực hiện hành động
2. **User ID** - ID của người dùng
3. **Username** - Tên người dùng (@username)
4. **Full Name** - Tên đầy đủ của người dùng
5. **Chat ID** - ID của cuộc trò chuyện
6. **Chat Type** - Loại chat (private/group/supergroup)
7. **Action** - Lệnh/hành động được thực hiện
8. **Details** - Chi tiết cơ bản về hành động

### Log Riêng (stock.log, aug.log, etc.):
**INFO Level** - Actions thành công:
- **stock.log**: Symbol queried, price, change %, stocks added/removed, notification sent
- **aug.log**: Gold type (SJC/DOJI), prices, scheduled updates
- **tuvi.log**: Zodiac sign, day selected
- **lunar.log**: Conversion details (solar ↔ lunar dates)
- **taixiu.log**: Bet amount, dice results, win/loss, points, stats

**WARNING Level** - Cảnh báo:
- Invalid input (stock symbol not found, invalid commands)
- Failed validations

**ERROR Level** - Lỗi:
- Exception details
- Stack traces
- Failed operations

## 📋 Format Log

```
2026-01-24 10:30:45 log_helper.py:25 INFO: User: John Doe (@johndoe) | ID: 123456789 | Chat: -987654321 (group) | Action: /stock | Details: Symbol: VCB
```

## 🎯 Các Command Được Ghi Log

| Command | Mô tả | Details |
|---------|-------|---------|
| `/start` | Khởi động bot | User started bot |
| `/help` | Xem trợ giúp | User requested help |
| `/weather` | Xem thời tiết | User requested weather |
| `/horoscope` `/tuvi` | Xem tử vi | User requested horoscope |
| `/lunar` `/amlich` | Chuyển đổi lịch | User requested calendar conversion |
| `/stock` `/ck` | Xem giá chứng khoán | Symbol: {mã CK} |
| `/stockwatch` | Theo dõi chứng khoán | User opened stock watch menu |
| `/aug` | Xem giá vàng | Requested gold price: {sjc/doji/both} |
| `/taixiu` | Chơi game tài xỉu | User started taixiu game |
| `/xsmb` | Xổ số miền bắc | Date: {ngày} |
| `/simsimi` | Chat với bot | Question: {câu hỏi} |
| `/catfact` | Thông tin về mèo | User requested cat fact |
| `/sleep` | Tính giờ ngủ | User requested sleep time calculation |
| `/tet` | Đếm ngày đến Tết | User checked days to Tet |
| `/getid` | Lấy Chat ID | Chat ID: {id} |
| Unknown messages | Tin nhắn không hiểu | Text: {nội dung} |
| File uploads | Gửi file | Type: {loại file} |

## 🔧 Sử dụng Logger

### Import logger helper:
```python
from utils.log_helper import log_user_action
```

### Ghi log trong handler:
```python
@bot.message_handler(commands=['mycommand'])
def my_handler(message):
    # Ghi log ngay khi nhận lệnh
    log_user_action(message, "/mycommand", "Optional details here")
    
    # Xử lý logic của bạn...
```

### Tham số của `log_user_action`:
- **message**: Message object từ telebot
- **action**: Tên hành động (command hoặc chức năng)
- **details**: (Optional) Chi tiết thêm về hành động

## 📁 Vị Trí File Log

Tất cả file log được lưu trong thư mục `logs/` tại root của project:
```
bot-tele/
├── logs/
│   ├── bot_usage.log
│   ├── stock.log
│   ├── tuvi.log
│   ├── lunar.log
│   ├── taixiu.log
│   └── aug.log
```

## 🔍 Xem Log

### Xem toàn bộ log:
```bash
cat logs/bot_usage.log
```

### Xem log realtime:
```bash
tail -f logs/bot_usage.log
```

### Tìm kiếm log theo user ID:
```bash
grep "ID: 123456789" logs/bot_usage.log
```

### Tìm kiếm log theo command:
```bash
grep "Action: /stock" logs/bot_usage.log
```

## 📈 Phân Tích Log

Bạn có thể phân tích log để:
- Xem command nào được sử dụng nhiều nhất
- Theo dõi người dùng hoạt động
- Debug lỗi dựa trên timestamp
- Hiểu hành vi người dùng

## ⚙️ Cấu Hình Log Level

Trong [logs/logs.py](logs/logs.py), bạn có thể thay đổi log level:
```python
logger = logging.getLogger(name)
logger.setLevel(logging.INFO)  # Có thể đổi thành DEBUG, WARNING, ERROR
```

## 🎨 Ví Dụ Log Thực Tế

### bot_usage.log (Log chung):
```
2026-01-24 09:15:23 log_helper.py:25 INFO: User: Nam Tp (@namtp) | ID: 5427391210 | Chat: 5427391210 (private) | Action: /aug | Details: Requested gold price: both
2026-01-24 09:20:45 log_helper.py:25 INFO: User: John Doe (@johndoe) | ID: 123456789 | Chat: -4831500227 (group) | Action: /stock | Details: Symbol: VCB
2026-01-24 10:00:00 log_helper.py:25 INFO: User: Jane Smith (@janesmith) | ID: 987654321 | Chat: 987654321 (private) | Action: /taixiu | Details: User started taixiu game
```

### stock.log (Log riêng):
```
2026-01-24 09:20:45 stock.py:145 INFO: Stock query: VCB | Price: 95500 | Change: 2.15% | User: johndoe (ID: 123456789)
2026-01-24 09:25:30 stock.py:278 INFO: Added stocks: VCB, FPT, VNM | Total: 5 | User: johndoe (ID: 123456789)
2026-01-24 09:26:15 stock.py:360 INFO: Stock removed: VNM | Remaining: 4 | User: johndoe (ID: 123456789)
2026-01-24 09:30:00 stock.py:115 ERROR: Error sending notification to 123456789: Connection timeout
```

### aug.log (Log riêng):
```
2026-01-24 09:15:00 aug.py:35 INFO: Scheduled gold price update started at 9:15 AM
2026-01-24 09:15:02 aug.py:25 INFO: Gold price sent: SJC | Buy: 77.50 | Sell: 78.00 | Chat: 5427391210
2026-01-24 09:15:03 aug.py:25 INFO: Gold price sent: DOJI | Buy: 77.40 | Sell: 77.90 | Chat: 5427391210
2026-01-24 09:15:05 aug.py:42 INFO: Scheduled gold prices sent successfully to chat 5427391210
2026-01-24 10:30:15 aug.py:57 INFO: Manual gold price request: sjc | User: namtp (ID: 5427391210)
```

### taixiu.log (Log riêng):
```
2026-01-24 10:00:30 taixiu.py:128 INFO: Game played: Choice=TÀI | Bet=1000 | Dice=4+5+6=15 | Result=TÀI | Win=True | NewPoints=6000 | User: janesmith (ID: 987654321)
2026-01-24 10:01:45 taixiu.py:128 INFO: Game played: Choice=XỈU | Bet=500 | Dice=2+3+2=7 | Result=XỈU | Win=True | NewPoints=6500 | User: janesmith (ID: 987654321)
2026-01-24 10:05:00 taixiu.py:263 INFO: Stats displayed: Games=15 | Wins=9 | WinRate=60.0% | Points=6500 | User: janesmith (ID: 987654321)
```

### tuvi.log (Log riêng):
```
2026-01-24 11:00:00 horoscope.py:51 INFO: Horoscope retrieved: Aries | Day: today | User: alice (ID: 111222333)
2026-01-24 11:05:00 horoscope.py:51 INFO: Horoscope retrieved: Leo | Day: tomorrow | User: bob (ID: 444555666)
```

### lunar.log (Log riêng):
```
2026-01-24 11:30:00 lunar_calendar.py:48 INFO: Today conversion: Solar 24/01/2026 -> Lunar 26/12/2025 | User: charlie (ID: 777888999)
2026-01-24 11:35:00 lunar_calendar.py:167 INFO: Conversion: 29/01/2026 (dương lịch sang âm lịch) -> 01/01/2026 | User: charlie (ID: 777888999)
```

---
✅ **Hệ thống logging đã được cấu hình hoàn chỉnh và sẵn sàng sử dụng!**
