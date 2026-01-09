import schedule
import config
from datetime import datetime
from utils.scheduler import start_scheduler

def send_lunch_reminder(bot):
    """Send a reminder to register for lunch only on weekdays"""
    # Check if today is Saturday (5) or Sunday (6)
    current_day = datetime.now().weekday()
    if current_day >= 5:  # 5 = Saturday, 6 = Sunday
        print(f"Today is weekend (day {current_day}), skipping lunch reminder")
        return
    
    # Replace with your target chat ID (can be stored in config.py)
    chat_ids = config.REMINDER_CHAT_IDS  # List of chat IDs to send reminder to
    
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, "⏰ Nhắc nhở: Hãy đăng kí ăn trưa hôm nay!")
        except Exception as e:
            print(f"Failed to send reminder to {chat_id}: {e}")

def register_handlers(bot):
    """Register the lunch reminder scheduler"""
    # Schedule the reminder for 9:00 AM every day
    schedule.every().day.at("09:00").do(send_lunch_reminder, bot)
    
    # Start the global scheduler thread
    start_scheduler()
    
    print("Lunch reminder scheduled for 9:00 AM on weekdays (Monday-Friday)")