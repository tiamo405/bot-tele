# Function
- Sleep
- chat bot: simimi
- xem tu vi
- xsmb
# Use
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
# Install
- Lib: pip install pyTelegramBotAPI
- token bot: [guide](https://help.ladipage.vn/form-data/cac-buoc-cai-dat-luu-data/luu-data-ve-telegram/huong-dan-tao-token-va-group-id-o-telegram)
- create file: config.py
  ```
  BOT_TOKEN = ""
  WEATHER_KEY = ""
  REMINDER_CHAT_IDS = [] # chứa các id nhóm, cách lấy id nhóm: sau khi add bot xong chạy /getid
  API_KEY_1TOUCH = "" 
  ```
- run
  ```
  python app.py
  ```

# Docker
- build images
```
docker build -t tele:0.0.1 .
```
- run container
```
docker run --restart=always -dit --ipc=host --net=host --privileged --name tele -v $(pwd):/app  tele:latest
```

# Docker compose
```sh
docker compose up -d
```