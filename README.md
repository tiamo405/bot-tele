# Function
- Sleep
- chat bot: simimi
- xem tu vi
- xsmb
# Use
- help
  ```
    /help
  ```
- Sleep
  ```
  /sleep or /Sleep
  ```
- Chat bot
  ```
  /sim How are you?
  ```
- Tu vi
  ```
  /tuvi or /horoscope
  ```
- Xo so mien Bac
  ```
  /xsmb
  ```
- convert lunar <-> solar
  ```
  /lunar
  ```
- linh tinh
  ```
  /catfact 
  /weather (HN)
  /taixiu
  ```
- Stock (Chứng khoán)
  ```
  /stock VCB           # Xem giá chứng khoán mã VCB
  /stockwatch          # Quản lý theo dõi chứng khoán (thêm/xóa/xem danh sách)
                       # Bot tự động gửi giá mỗi 5 phút (T2-T6, 9h-15h)
  ```
# Install
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Token bot: [guide](https://help.ladipage.vn/form-data/cac-buoc-cai-dat-luu-data/luu-data-ve-telegram/huong-dan-tao-token-va-group-id-o-telegram)
- Create file `.env` (copy from `.env.example` if available):
  ```env
  BOT_TOKEN = "your_bot_token_here"
  WEATHER_KEY = "your_weather_api_key_here"
  REMINDER_CHAT_IDS = [id]
  REMINDER_CHAT_IDS_BADMINTON = [id]
  REMINDER_CHAT_IDS_TET = [id]
  API_KEY_1TOUCH = "your_1touch_api_key_here"
  ```
  **Note:** File `.env` chứa thông tin nhạy cảm, không commit lên git
- Run:
  ```bash
  python app.py
  ```

# Docker

## Cách build với Base Image (khuyến nghị - nhanh hơn)

Base image giúp cache các dependencies, chỉ cần build lại khi `requirements.txt` thay đổi.

### Lần đầu tiên:
1. Build base image (chỉ cần build 1 lần hoặc khi requirements.txt thay đổi):
```bash
docker build -f Dockerfile.base -t tele-base:latest .
```

2. Build app image (nhanh hơn vì đã có base):
```bash
docker build --rm --force-rm -t tele:latest .
```

### Lần sau (khi code thay đổi):
```bash
# Chỉ cần build app image (rất nhanh)
docker build --rm --force-rm -t tele:latest .
```

### Khi requirements.txt thay đổi:
```bash
# Build lại base image
docker build -f Dockerfile.base -t tele-base:latest .

# Sau đó build app image
docker build --rm --force-rm -t tele:latest .
```

## Cách build thông thường (không dùng base image)
- Build images (tự động xóa intermediate containers)
```bash
docker build --rm --force-rm -t tele:latest .
```
- Run container
```bash
docker run --restart=always -dit --ipc=host --net=host --privileged --name tele -v $(pwd):/app  tele:latest
```
- Xóa images cũ không dùng (dangling images)
```bash
docker image prune -f
```

# Docker compose
- Build và chạy (rebuild khi code thay đổi)
```bash
# Build lại image mới (xóa cache)
docker compose build --no-cache

# Khởi động container
docker compose up -d

# Xem logs
docker logs -f telegram-bot
```

- Build lại từ đầu (xóa container + volumes cũ)
```bash
# Dừng và xóa containers, networks, volumes
docker compose down -v

# Build lại image mới
docker compose build --no-cache

# Khởi động lại
docker compose up -d
```

- Dọn dẹp images cũ sau khi build
```bash
# Sau khi build xong, xóa các images không dùng (dangling)
docker image prune -f

# Hoặc xóa toàn bộ images không được container nào sử dụng
docker image prune -a -f

# Xóa toàn bộ cache build (tiết kiệm dung lượng)
docker builder prune -f
```

- Script build nhanh (build + cleanup tự động)
```bash
# Tạo file build.sh
cat > build.sh << 'EOF'
#!/bin/bash
echo "🔨 Building new image..."
docker compose build --no-cache

echo "🧹 Cleaning up old images..."
docker image prune -f

echo "🚀 Starting containers..."
docker compose up -d

echo "✅ Done! Checking logs..."
docker logs --tail 50 telegram-bot
EOF

chmod +x build.sh
./build.sh
```