import schedule
import time
import threading
import config
from datetime import datetime

def send_badminton_reminder(bot):
    """Send a reminder to register for badminton only on weekdays"""
    # Check if today is Saturday (5) or Sunday (6)
    current_day = datetime.now().weekday()
    # if current_day >= 5:  # 5 = Saturday, 6 = Sunday
    #     print(f"Today is weekend (day {current_day}), skipping lunch reminder")
    #     return
    if current_day < 6 : # 6 = Sunday
        print(f"Today is weekday (day {current_day}), skipping badminton reminder")
        # return
    
    # Replace with your target chat ID (can be stored in config.py)
    chat_ids = config.REMINDER_CHAT_IDS_BADMINTON  # List of chat IDs to send reminder to
    
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, "⏰ Nhắc nhở: Hãy đăng kí chơi cầu lông hôm nay!")
        except Exception as e:
            print(f"Failed to send reminder to {chat_id}: {e}")

def schedule_checker(bot):
    """Function that runs in a separate thread to check schedules"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def register_handlers(bot):
    """Register the badminton reminder scheduler"""
    # Schedule the reminder for 21:00 every Sunday
    schedule.every().sunday.at("21:00").do(send_badminton_reminder, bot)
    
    # Start the scheduler in a separate thread
    reminder_thread = threading.Thread(target=schedule_checker, args=(bot,))
    reminder_thread.daemon = True  # Thread will exit when main program exits
    reminder_thread.start()
    
    print("Badminton reminder scheduled for 21:00 on Sundays")