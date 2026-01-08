import schedule
import time
import threading
import config
from datetime import datetime

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

def handle_tet_command(message, bot):
    """Handle /tet command to show days until Lunar New Year"""
    days_remaining = get_days_to_tet()
    
    if days_remaining > 0:
        message_text = f"🎊 Chỉ còn {days_remaining} ngày nữa là đến Tết Âm Lịch 2026! 🎊"
    elif days_remaining == 0:
        message_text = "🎉 Hôm nay là Tết Âm Lịch! Chúc mừng năm mới! 🎉"
    else:
        message_text = f"🎊 Tết Âm Lịch đã qua {abs(days_remaining)} ngày rồi! 🎊"
    
    bot.reply_to(message, message_text)

def schedule_checker(bot):
    """Function that runs in a separate thread to check schedules"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def register_handlers(bot):
    """Register the Tet reminder scheduler and command handler"""
    # Register /tet command handler
    @bot.message_handler(commands=['tet'])
    def tet_command(message):
        handle_tet_command(message, bot)
    
    # Schedule the reminder for 9:00 AM every day
    schedule.every().day.at("09:00").do(send_tet_reminder, bot)
    
    # Start the scheduler in a separate thread
    reminder_thread = threading.Thread(target=schedule_checker, args=(bot,))
    reminder_thread.daemon = True  # Thread will exit when main program exits
    reminder_thread.start()
    
    print("Tet reminder scheduled for 9:00 AM every day")
