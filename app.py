from telebot import TeleBot
import config
import time
from handlers import gold, start, help, horoscope, time_sleep, simsimi, catfact, weather, lunch_reminder, xsmb, taixiu, lunar_calendar, badminton_reminder, tet_reminder, tet_command, stock, silver
from utils.log_helper import log_user_action

# Khởi tạo bot
bot = TeleBot(config.BOT_TOKEN)

# Đăng ký các handler
start.register_handlers(bot)
help.register_handlers(bot)
horoscope.register_handlers(bot)
time_sleep.register_handlers(bot)
simsimi.register_handlers(bot)
catfact.register_handlers(bot)
weather.register_handlers(bot)
# lunch_reminder.register_handlers(bot)
badminton_reminder.register_handlers(bot)
tet_reminder.register_handlers(bot)
tet_command.register_handlers(bot)
xsmb.register_handlers(bot)
taixiu.register_handlers(bot)
lunar_calendar.register_handlers(bot)
stock.register_handlers(bot)
gold.register_handlers(bot)
silver.register_handlers(bot)

@bot.message_handler(commands=["getid"])
def handle_get_id(message):
    log_user_action(message, "/getid", f"Chat ID: {message.chat.id}")
    bot.reply_to(message, f"Chat ID của nhóm này là: `{message.chat.id}`", parse_mode="Markdown")
    
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    log_user_action(message, "unknown_message", f"Text: {message.text}")
    bot.reply_to(message, 'Tôi không hiểu câu lệnh của bạn.')

@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    log_user_action(message, "file_upload", f"Type: {message.content_type}")
    bot.reply_to(message.chat.id, 'gui file del gi day')


if __name__ == '__main__':
    print("Bot đang chạy...")
    
    # Retry logic để xử lý lỗi network
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Lỗi polling: {e}")
            print("Đang thử kết nối lại sau 5 giây...")
            time.sleep(5)
