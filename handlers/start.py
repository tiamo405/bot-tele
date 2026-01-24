import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.log_helper import log_user_action

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        log_user_action(message, "/start", "User started bot")
        bot.reply_to(message, "Chào mừng bạn đến với bot! Nhập /help để xem các lệnh có sẵn.")
