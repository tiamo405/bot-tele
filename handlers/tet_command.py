from datetime import datetime

def get_days_to_tet():
    """Calculate days remaining until Lunar New Year"""
    tet_date = datetime(2026, 2, 17)
    current_date = datetime.now()
    days_remaining = (tet_date - current_date).days
    return days_remaining

def register_handlers(bot):
    """Register /tet command handler"""
    
    @bot.message_handler(commands=['tet'])
    def tet_command(message):
        """Handle /tet command to show days until Lunar New Year"""
        days_remaining = get_days_to_tet()
        
        if days_remaining > 0:
            message_text = f"🎊 Chỉ còn {days_remaining} ngày nữa là đến Tết Âm Lịch 2026! 🎊 \n Còn {days_remaining - 3} ngày nữa là được nghỉ lễ "
        elif days_remaining == 0:
            message_text = "🎉 Hôm nay là Tết Âm Lịch! Chúc mừng năm mới! 🎉"
        else:
            message_text = f"🎊 Tết Âm Lịch đã qua {abs(days_remaining)} ngày rồi! 🎊"
        
        bot.reply_to(message, message_text)
    
    print("/tet command handler registered")
