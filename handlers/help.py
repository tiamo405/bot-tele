def register_handlers(bot):
    @bot.message_handler(commands=['help'])
    def handle_help(message):
        bot.reply_to(
            message,
            "Danh sách các lệnh:\n"
            "/start - Bắt đầu tương tác với bot\n"
            "/help - Hiển thị danh sách lệnh\n"
            "/horoscope - Xem tử vi\n"
            "/xsmb - Xem kết quả xổ số miền Bắc(/xsmb dd-mm-yyyy để chọn ngày)\n"
            "/simsimi text - Trò chuyện với bot Simsimi\n"
            "/catfact - Nhận thông tin về mèo\n"
            "/weather - Xem thời tiết\n"
            "/sleep - Tính giờ ngủ\n"
        )
