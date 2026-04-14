import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.silver import get_silver
from utils.log_helper import log_user_action
from logs.logs import setup_logger
import schedule
from utils.scheduler import start_scheduler
import config
from utils.notification_registry import get_chat_ids

silver_log = setup_logger('silver.log')

def format_silver_message(silver_data):
    """Format silver price data into a message"""
    message = f"🪙 *Giá Bạc Thế Giới*\n\n"
    message += f"💵 *Giá bạc (USD/oz):*\n"
    message += f"  • {silver_data.get('price_usd_agu', 'N/A')} USD/oz\n"

    # Giá bạc Ancarat (nếu có)
    message += f"\n🏪 *Giá bạc Ancarat:*\n"
    message += f"  • Tên: {silver_data.get('name_ancarat', 'N/A')}\n"
    message += f"  • {silver_data.get('price_ancarat', 'N/A')} VND\n"
    return message

def send_silver_price(bot, chat_id):
    """Send silver price to a chat"""
    try:
        silver_data = get_silver()
        message = format_silver_message(silver_data)
        bot.send_message(chat_id, message, parse_mode="Markdown")
        silver_log.info(f"Silver price sent: {silver_data.get('price_usd_agu', 'N/A')} USD/oz | Chat: {chat_id}")
    except Exception as e:
        silver_log.error(f"Error sending silver price to {chat_id}: {str(e)}")
        bot.send_message(chat_id, f"❌ Lỗi khi lấy giá bạc: {str(e)}")

def send_scheduled_silver_price(bot):
    """Send silver price to scheduled chat IDs"""
    silver_log.info(f"Scheduled silver price update started")
    for chat_id in get_chat_ids("schedule_silver"):
        try:
            silver_data = get_silver()
            message = format_silver_message(silver_data)
            bot.send_message(chat_id, message, parse_mode="Markdown")
            silver_log.info(f"Scheduled silver price sent successfully to chat {chat_id}")
        except Exception as e:
            silver_log.error(f"Error sending scheduled silver price to {chat_id}: {str(e)}")

def register_handlers(bot):
    @bot.message_handler(commands=['bac'])
    def handle_silver(message):
        # Log user action
        log_user_action(message, "/bac", "Requested silver price")
        silver_log.info(f"Manual silver price request | User: {message.from_user.username} (ID: {message.from_user.id})")
        
        # Send silver price
        send_silver_price(bot, message.chat.id)
    
    # Setup scheduled task at 9:00 AM (if needed)
    if get_chat_ids("schedule_silver"):
        schedule.every().day.at("09:00").do(lambda: send_scheduled_silver_price(bot))
        start_scheduler()
        print("Scheduled silver price update at 9:00 AM daily")