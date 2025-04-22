from telebot import TeleBot
import config
from handlers import start, help, horoscope, time_sleep, simsimi, catfact, weather

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

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, 'Tôi không hiểu câu lệnh của bạn.')

@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    bot.reply_to(message.chat.id, 'gui file del gi day')

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
