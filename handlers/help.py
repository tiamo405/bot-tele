import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.log_helper import log_user_action

def register_handlers(bot):
    @bot.message_handler(commands=['help'])
    def handle_help(message):
        log_user_action(message, "/help", "User requested help")
        help_text = (
            "🤖 **DANH SÁCH LỆNH BOT** 🤖\n\n"
            "🚀 **/start** - Bắt đầu tương tác với bot\n"
            "❓ **/help** - Hiển thị danh sách lệnh\n"
            "🔮 **/horoscope** - Xem tử vi cung hoàng đạo\n"
            "🗓️ **/lunar** - Chuyển đổi dương lịch ⇄ âm lịch\n"
            "🎲 **/xsmb** - Xem kết quả xổ số miền Bắc\n"
            "💬 **/simsimi** - Trò chuyện với bot Simsimi\n"
            "🐱 **/catfact** - Nhận thông tin thú vị về mèo\n"
            "🌤️ **/weather** - Xem thời tiết hiện tại\n"
            "😴 **/sleep** - Tính giờ ngủ lý tưởng\n"
            "🎰 **/taixiu** - Chơi game tài xỉu vui vẻ\n"
            "📊 **/taixiustats** - Xem thống kê game tài xỉu\n"
            "📈 **/stock vcb** or **/chungkhoan vcb** or **/chung vcb** or **/ck vcb** - Xem giá chứng khoán\n"
            "📊 **/stockwatch** or **/theodoick** or **/ckwatch** - Theo dõi giá chứng khoán\n\n"
            "💰 **/vang** - Xem giá vàng\n"
            "🪙 **/bac** - Xem giá bạc\n\n"
            "🗓️ **CHUYỂN ĐỔI LỊCH:**\n"
            "• 🌞 Dương lịch → Âm lịch\n"
            "• 🌙 Âm lịch → Dương lịch\n"
            "• 📅 Xem ngày hôm nay\n"
            "• 🎋 Hiển thị can chi\n\n"
            "🎮 **GAME TÀI XỈU:**\n"
            "• Mỗi người chơi bắt đầu với 5,000 điểm\n"
            "• Chọn TÀI (11-18) hoặc XỈU (3-10)\n"
            "• Đặt cược và thử vận may!\n"
            "• Thắng = nhận điểm, thua = mất điểm\n\n"
            "📈 **CHỨNG KHOÁN:**\n"
            "• Xem giá: `/stock VCB`\n"
            "• Hiển thị giá trần, sàn, tham chiếu, hiện tại\n"
            "• Thêm/xóa mã theo dõi: `/stockwatch`\n"
            "• Nhận thông báo giá mỗi 5 phút (T2-T6, 9h-15h)\n\n"
            "✨ **Chúc bạn sử dụng bot vui vẻ!**"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown")
