import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logs.logs import setup_logger

# Logger chung cho bot
bot_logger = setup_logger('bot_usage.log')

def log_user_action(message, action, details=""):
    """
    Ghi log hành động của user
    
    Args:
        message: Message object từ telebot
        action: Tên hành động (command hoặc chức năng)
        details: Chi tiết thêm về hành động
    """
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or "No name"
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    log_message = f"User: {full_name} (@{username}) | ID: {user_id} | Chat: {chat_id} ({chat_type}) | Action: {action}"
    if details:
        log_message += f" | Details: {details}"
    
    bot_logger.info(log_message)
