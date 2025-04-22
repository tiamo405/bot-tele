def register_handlers(bot):
    @bot.message_handler(commands=['help'])
    def handle_help(message):
        bot.reply_to(
            message,
            "Danh sách các lệnh:\n"
            "/start - Bắt đầu tương tác với bot\n"
            "/help - Hiển thị danh sách lệnh\n"
            "/horoscope - Xem tử vi"
        )
