import schedule
import time
import threading
import config
from datetime import datetime

def send_tet_reminder(bot):
    """Send a reminder about days until Lunar New Year"""
    # Lunar New Year 2026 is on February 17, 2026
    tet_date = datetime(2026, 2, 17)
    current_date = datetime.now()
    
    # Calculate days remaining
    days_remaining = (tet_date - current_date).days
    
    # Prepare message based on days remaining
    if days_remaining > 0:
        message = f"🎊 Chỉ còn {days_remaining} ngày nữa là đến Tết Âm Lịch 2026! 🎊"
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

def schedule_checker(bot):
    """Function that runs in a separate thread to check schedules"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def register_handlers(bot):
    """Register the Tet reminder scheduler"""
    # Schedule the reminder for 9:00 AM every day
    schedule.every().day.at("09:00").do(send_tet_reminder, bot)
    
    # Start the scheduler in a separate thread
    reminder_thread = threading.Thread(target=schedule_checker, args=(bot,))
    reminder_thread.daemon = True  # Thread will exit when main program exits
    reminder_thread.start()
    
    print("Tet reminder scheduled for 9:00 AM every day")
