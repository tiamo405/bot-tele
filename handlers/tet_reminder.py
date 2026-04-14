import schedule
import config
from datetime import datetime
from utils.scheduler import start_scheduler
from utils.notification_registry import get_chat_ids

def get_days_to_tet():
    """Calculate days remaining until Lunar New Year"""
    tet_date = datetime(2026, 4, 25)
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
        message = f"🎊 Chỉ còn {days_remaining} ngày nữa là đến Giỗ tổ Hùng Vương! 🎊 \n Chỉ còn {days_remaining + 5} ngày nữa là được nghỉ 30/4 1/5"
    else:
        # After Tet has passed , break no message
        return

        
    
    # Get chat IDs from config
    chat_ids = get_chat_ids("reminder_tet")
    
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


if __name__ == "__main__":
    # For testing purposes, you can run the reminder directly
    # Note: In production, this will be scheduled by the main app
    days_remaining = get_days_to_tet()
    print(f"Days remaining until Gio to Hung Vuong: {days_remaining}")