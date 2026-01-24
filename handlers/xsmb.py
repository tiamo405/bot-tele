import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.xsmb import get_xsmb
from utils.log_helper import log_user_action
from datetime import datetime

def register_handlers(bot):
    @bot.message_handler(commands=['xsmb'])
    def handle_xsmb(message):
        date = '-'.join(map(str, (message.text.split()[1:])))
        log_user_action(message, "/xsmb", f"Date: {date if date else 'latest'}")
        if date:
            answer = get_xsmb(date)
        else:  # Nếu không có ngày, lấy kết quả mới nhất, điền ngày hôm nay nếu > 19h hoặc lấy của ngày liên trước
            now = datetime.now()
            if now.hour >= 19:
                date = now.strftime("%d-%m-%Y")
            else:
                # Lấy ngày hôm qua nếu trước 19h vi chua co kết quả
                yesterday = now.replace(day=now.day - 1)
                date = yesterday.strftime("%d-%m-%Y")
            answer = get_xsmb(date)
        bot.send_message(message.chat.id, answer)
        