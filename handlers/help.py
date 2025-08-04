def register_handlers(bot):
    @bot.message_handler(commands=['help'])
    def handle_help(message):
        help_text = (
            "🤖 **DANH SÁCH LỆNH BOT** 🤖\n\n"
            "🚀 **/start** - Bắt đầu tương tác với bot\n"
            "❓ **/help** - Hiển thị danh sách lệnh\n"
            "🔮 **/horoscope** - Xem tử vi cung hoàng đạo\n"
            "🎲 **/xsmb** - Xem kết quả xổ số miền Bắc\n"
            "💬 **/simsimi** - Trò chuyện với bot Simsimi\n"
            "🐱 **/catfact** - Nhận thông tin thú vị về mèo\n"
            "🌤️ **/weather** - Xem thời tiết hiện tại\n"
            "😴 **/sleep** - Tính giờ ngủ lý tưởng\n"
            "🎰 **/taixiu** - Chơi game tài xỉu vui vẻ\n"
            "📊 **/taixiustats** - Xem thống kê game tài xỉu\n\n"
            "🎮 **GAME TÀI XỈU:**\n"
            "• Mỗi người chơi bắt đầu với 5,000 điểm\n"
            "• Chọn TÀI (11-18) hoặc XỈU (3-10)\n"
            "• Đặt cược và thử vận may!\n"
            "• Thắng = nhận điểm, thua = mất điểm\n\n"
            "✨ **Chúc bạn sử dụng bot vui vẻ!**"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown")
