# Hướng dẫn Deploy Bot Telegram

## � Cách 1: Setup tự động (Khuyến nghị)

```bash
# 1. Download script và files cần thiết
wget https://raw.githubusercontent.com/your-repo/setup-server.sh
wget https://raw.githubusercontent.com/your-repo/docker-compose.yml

# 2. Tạo file .env (cập nhật API keys của bạn)
cat > .env << 'EOF'
BOT_TOKEN = "your_bot_token_here"
WEATHER_KEY = "your_weather_key_here"
API_KEY_1TOUCH = "your_1touch_api_key"
VNSTOCK_API_KEY = "your_vnstock_api_key"
EOF

# 3. Chạy script tự động
chmod +x setup-server.sh
./setup-server.sh

# 4. Cập nhật chat IDs trong data/chat_ids.json, sau đó chạy:
docker compose up -d
```

## 📦 Cách 2: Setup thủ công

### �📦 Chuẩn bị trên Server mới

### 1. Tạo cấu trúc thư mục
```bash
mkdir -p bot-tele/data bot-tele/logs
cd bot-tele
```

> **⚠️ QUAN TRỌNG - Folder logs/ chứa code Python!**
> - Folder `logs/` vừa chứa code (`logs.py`, `__init__.py`) vừa chứa log files
> - Phải copy file code từ image ra TRƯỚC khi mount để tránh mất file
> - Các bước bên dưới sẽ hướng dẫn chi tiết

### 2. Tạo các file cần thiết

#### File `.env`
```bash
cat > .env << 'EOF'
BOT_TOKEN = "your_bot_token_here"
WEATHER_KEY = "your_weather_key_here"
API_KEY_1TOUCH = "your_1touch_api_key"
VNSTOCK_API_KEY = "your_vnstock_api_key"
EOF
```

#### File `docker-compose.yml`
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  bot-tele:
    image: namtiamo/tele:latest
    container_name: telegram-bot
    restart: unless-stopped
    environment:
      - TZ=Asia/Ho_Chi_Minh
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    network_mode: host
    dns:
      - 8.8.8.8
      - 1.1.1.1
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF
```

#### File `data/chat_ids.json`
```bash
cat > data/chat_ids.json << 'EOF'
{
  "reminder_lunch": [YOUR_CHAT_ID],
  "reminder_badminton": [YOUR_CHAT_ID],
  "reminder_tet": [YOUR_CHAT_ID],
  "schedule_aug": [YOUR_CHAT_ID],
  "schedule_silver": [YOUR_CHAT_ID]
}
EOF
```

### 3. Copy file code Python từ image ra host

**⚠️ BƯỚC QUAN TRỌNG** - Phải làm TRƯỚC KHI chạy docker-compose:

```bash
# Pull image
docker pull namtiamo/tele:latest

# Tạo container tạm để copy file
docker create --name temp-bot namtiamo/tele:latest
docker cp temp-bot:/app/logs/logs.py ./logs/
docker cp temp-bot:/app/logs/__init__.py ./logs/
docker rm temp-bot

# Kiểm tra đã có file chưa
ls -la logs/
# Phải thấy: __init__.py và logs.py
```

### 4. Chạy Bot
```bash
# Pull image mới nhất (nếu chưa pull ở bước 3)
docker pull namtiamo/tele:latest

# Khởi động bot
docker compose up -d

# Xem logs
docker compose logs -f

# Hoặc xem log file trực tiếp
tail -f logs/bot_usage.log
```

## 🔄 Cập nhật Bot

```bash
# Pull image mới
docker pull namtiamo/tele:latest

# Restart container
docker compose down
docker compose up -d
```

## 📊 Quản lý Data

### Data được lưu trên server (mount vào container)
- `data/chat_ids.json` - Danh sách chat IDs
- `data/stock_subscriptions.json` - Đăng ký theo dõi cổ phiếu
- `data/taixiu_users.json` - Dữ liệu game tài xỉu

### Logs được mount ra host (cần copy file code trước)
- `logs/__init__.py` - Python module init (code)
- `logs/logs.py` - Python logging module (code)
- `logs/*.log` - Runtime log files (data)

> **⚠️ QUAN TRỌNG KHI DEPLOY MỚI:**
> 1. Phải copy file `logs.py` và `__init__.py` từ image ra host TRƯỚC
> 2. Nếu folder logs/ rỗng khi mount → mất file .py → lỗi import
> 3. Xem hướng dẫn ở bước 3 trong phần "Chuẩn bị trên Server mới"

### Backup data
```bash
# Backup cả data và logs
tar -czf bot-backup-$(date +%Y%m%d).tar.gz data/ logs/

# Chỉ backup data (không backup file .py)
tar -czf bot-data-backup-$(date +%Y%m%d).tar.gz data/ logs/*.log
```

### Restore data
```bash
tar -xzf bot-data-backup-YYYYMMDD.tar.gz
```

## 🔍 Troubleshooting

### Kiểm tra container đang chạy
```bash
docker ps
```

### Xem logs
```bash
# Cách 1: Xem log file trực tiếp trên host
tail -f logs/bot_usage.log
tail -f logs/stock.log

# Cách 2: Xem Docker container logs
docker compose logs -f bot-tele

# Cách 3: Xem logs trong container
docker compose exec bot-tele ls -la /app/logs/
docker compose exec bot-tele tail -f /app/logs/bot_usage.log
```

### Restart bot
```bash
docker compose restart
```

### Kiểm tra file mount
```bash
docker compose exec bot-tele ls -la /app/data/
docker compose exec bot-tele ls -la /app/logs/
```

## 📝 Lưu ý quan trọng

1. **File .env**: Chứa API keys, KHÔNG được commit vào Git
2. **Folder data/**: Chứa dữ liệu runtime, mỗi server có data riêng
3. **Docker image**: CHỈ chứa code, KHÔNG chứa data hay logs
4. **Volume mount**: Data từ server sẽ mount vào container, ghi đè data trong image
