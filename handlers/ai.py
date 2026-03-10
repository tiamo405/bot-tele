import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_api.ai import ask_ai
from utils.log_helper import log_user_action
from logs.logs import setup_logger

logger = setup_logger('ai.log')

def register_handlers(bot):
    @bot.message_handler(commands=['ai'])
    def handle_ai(message):
        try:
            # Lấy câu hỏi từ message
            question = message.text.replace('/ai', '').strip()
            
            # Kiểm tra xem có câu hỏi không
            if not question:
                bot.reply_to(
                    message, 
                    "❓ Vui lòng nhập câu hỏi sau lệnh /ai\n\n"
                    "📝 *Ví dụ:*\n"
                    "• `/ai Giải thích về Python`\n"
                    "• `/ai Viết code tính giai thừa`\n"
                    "• `/ai Sự khác biệt giữa list và tuple`",
                    parse_mode="Markdown"
                )
                log_user_action(message, "/ai", "Empty question")
                return
            
            log_user_action(message, "/ai", f"Question: {question[:50]}...")
            
            # Gửi typing indicator để user biết bot đang xử lý
            bot.send_chat_action(message.chat.id, 'typing')
            
            # Gọi API AI
            answer = ask_ai(question)
            
            # Telegram có giới hạn 4096 ký tự/message
            if len(answer) > 4096:
                # Chia nhỏ response nếu quá dài
                chunks = [answer[i:i+4096] for i in range(0, len(answer), 4096)]
                for chunk in chunks:
                    bot.send_message(message.chat.id, chunk, parse_mode="Markdown")
            else:
                bot.reply_to(message, answer, parse_mode="Markdown")
            
            logger.info(f"AI response sent to user {message.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error in AI handler: {str(e)}")
            bot.reply_to(
                message, 
                f"⚠️ Đã xảy ra lỗi khi xử lý câu hỏi:\n`{str(e)}`",
                parse_mode="Markdown"
            )
