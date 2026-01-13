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
- Lib: pip install pyTelegramBotAPI
- token bot: [guide](https://help.ladipage.vn/form-data/cac-buoc-cai-dat-luu-data/luu-data-ve-telegram/huong-dan-tao-token-va-group-id-o-telegram)
- create file: config.py
  ```
  BOT_TOKEN = ""
  WEATHER_KEY = ""
  REMINDER_CHAT_IDS = []
  REMINDER_CHAT_IDS_BADMINTON = []
  REMINDER_CHAT_IDS_TET = []  # Chat IDs for Tet reminders
  ```
- run
  ```
  python app.py
  ```

# Docker
- build images
```
docker build -t tele:latest .
```
- run container
```
docker run --restart=always -dit --ipc=host --net=host --privileged --name tele -v $(pwd):/app  tele:latest
```

# Docker compose
```sh
docker compose build --no-cache
docker compose up -d
```