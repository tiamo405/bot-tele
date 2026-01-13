import schedule
import config
from datetime import datetime
from utils.scheduler import start_scheduler

def get_days_to_tet():
    """Calculate days remaining until Lunar New Year"""
    tet_date = datetime(2026, 2, 17)
    current_date = datetime.now()
    days_remaining = (tet_date - current_date).days
    return days_remaining

def send_tet_reminder(bot):
    """Send a reminder about days until Lunar New Year only on weekdays"""
    # Check if today is Saturday (5) or Sunday (6)
    current_day = datetime.now().weekday()
    if current_day >= 5:  # 5 = Saturday, 6 = Sunday
        print(f"Today is weekend (day {current_day}), skipping Tet reminder")
        return
    
    # Calculate days remaining
    days_remaining = get_days_to_tet()
    
    # Prepare message based on days remaining
    if days_remaining > 0:
        message = f"🎊 Chỉ còn {days_remaining} ngày nữa là đến Tết Âm Lịch 2026! 🎊 \n Chỉ còn {days_remaining - 3} ngày nữa là được nghỉ"
    else:
        # After Tet has passed , break no message
        return

        
    
    # Get chat IDs from config
    chat_ids = config.REMINDER_CHAT_IDS_TET  # List of chat IDs to send reminder to
    
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Failed to send Tet reminder to {chat_id}: {e}")

def register_handlers(bot):
    """Register the Tet reminder scheduler"""
    # Schedule the reminder for 8:30 AM every day
    schedule.every().day.at("08:30").do(send_tet_reminder, bot)
    
    # Start the global scheduler thread
    start_scheduler()
    
    print("Tet reminder scheduled for 8:30 AM on weekdays (Monday-Friday)")
