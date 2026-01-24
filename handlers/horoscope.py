import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logs.logs import setup_logger 
from get_api.get_horoscpoe import get_daily_horoscope
from utils.log_helper import log_user_action

tuvi_log = setup_logger('tuvi.log')

def register_handlers(bot):
    @bot.message_handler(commands=['horoscope', 'tuvi'])
    def sign_handler(message):
        log_user_action(message, "/horoscope", "User requested horoscope")
        markup = InlineKeyboardMarkup(row_width=3)
        zodiac_signs = [
            "Aries 21/3 - 19/4 (Bạch Dương)", "Taurus 20/4 - 20/5 (Kim Ngưu)", "Gemini 21/5 - 21/6(Sng Tử)", "Cancer 22/6 - 22/7 (Cự Giải)", "Leo 23/7 - 22/8(Sư Tử)", "Virgo 23/8 - 22/9(Xử Nữ)",
            "Libra 23/9 - 22/10(Thiên Bình)", "Scorpio 23/10 - 22/11(Thiên Yết)", "Sagittarius 23/11 - 21/12(Nhân Mã)", "Capricorn 22/12 - 19/1(Ma Kết)", "Aquarius 20/1 - 18/2(Bảo Bình)", "Pisces  19/2 - 20/3(Song Ngư)"
        ]
        buttons = [InlineKeyboardButton(text=sign, callback_data=f"sign_{sign}") for sign in zodiac_signs]
        markup.add(*buttons)

        bot.send_message(
            message.chat.id,
            "What's your zodiac sign? Choose one below:",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("sign_"))
    def choose_day(call):
        sign = call.data.split("_")[1]
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton(text="Today", callback_data=f"day_today_{sign}"),
            InlineKeyboardButton(text="Tomorrow", callback_data=f"day_tomorrow_{sign}"),
            InlineKeyboardButton(text="Yesterday", callback_data=f"day_yesterday_{sign}"),
        ]
        markup.add(*buttons)

        bot.send_message(
            call.message.chat.id,
            f"Great! You chose *{sign}*. Now, pick a day:",
            parse_mode="Markdown",
            reply_markup=markup
        )
    @bot.callback_query_handler(func=lambda call: call.data.startswith("day_"))
    def call_api(call):
        _, day, sign = call.data.split("_")
        sign = sign.split()[0]
        # Gọi hàm xử lý tử vi
        horoscope = get_daily_horoscope(sign, day.upper())
        data = horoscope["data"]
        horoscope_message = f'*Horoscope:* {data["horoscope_data"]}\n*Sign:* {sign}\n*Day:* {data["date"]}'
        
        # Log thành công
        tuvi_log.info(f"Horoscope retrieved: {sign} | Day: {day} | User: {call.from_user.username} (ID: {call.from_user.id})")
        
        # Gửi kết quả về cho người dùng
        bot.send_message(call.message.chat.id, horoscope_message)
