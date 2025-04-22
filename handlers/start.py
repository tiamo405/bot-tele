def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        bot.reply_to(message, "Chào mừng bạn đến với bot! Nhập /help để xem các lệnh có sẵn.")
