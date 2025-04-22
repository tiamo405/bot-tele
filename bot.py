# -*- coding: utf-8 -*-

import os
import telebot
import config
from utils import horoscope, time_sleeps
from get_api.get_answer_simsimi import get_answer_simsimi
# from get_api.xsmb import xsmb
from logs.logs import setup_logger 

# logger = setup_logger('logs.log')
simsimi_log = setup_logger("simsimi.log")
xsmb_log = setup_logger('xsmb_log.log')
# tuvi_log = setup_logger('tuvi.log')

BOT_TOKEN = config.BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello, how are you doing?")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "I'm here to help you. You can ask me about your horoscope, sleep cycle or ask me to chat with Simsimi. Just type /horoscope or /sleep or /simsimi to get started.")

#-------------------------
# xem bói tử vi cung hoàng đạo  + ngày
@bot.message_handler(commands=['horoscope', 'tuvi', 'Tuvi', 'Horoscope'])
def sign_handler(message):
    text = "What's your zodiac sign?\nChoose one: *Aries 21/3 - 19/4 (Bạch Dương)*, *Taurus 20/4 - 20/5 (Kim Ngưu)*, *Gemini 21/5 - 21/6(Sng Tử)*, *Cancer 22/6 - 22/7 (Cự Giải)*, *Leo 23/7 - 22/8(Sư Tử)*, *Virgo 23/8 - 22/9(Xử Nữ)*, *Libra 23/9 - 22/10(Thiên Bình)*, *Scorpio 23/10 - 22/11(Thiên Yết)*, *Sagittarius 23/11 - 21/12(Nhân Mã)*, *Capricorn 22/12 - 19/1(Ma Kết)*, *Aquarius 20/1 - 18/2(Bảo Bình)*, and *Pisces  19/2 - 20/3(Song Ngư)*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)

def day_handler(message):
    sign = message.text
    text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, horoscope.fetch_horoscope, sign.capitalize())
    


#----------------------------
# chat voi simsimi
@bot.message_handler(commands=['simsimi', 'sim'])
def start_simsimi(message) :
    quess = ' '.join(map(str, (message.text.split()[1:])))
    answer = get_answer_simsimi(quess)
    bot.send_message(message.chat.id, answer.json()['message'])
    simsimi_log.info('Quess: {}'.format(quess))
    simsimi_log.info('Answer: {}'.format(answer.json()['message']))



#-----------------------------------------------
# AI MidJourney
@bot.message_handler(commands=['draw'])
def aiMidJourney(message) :
    bot.send_message(message.chat.id, 'oke')


#--------------------------------------
# Sleep
@bot.message_handler(commands=['sleep', 'Sleep'])
def Sleep(message) :
    hours, minutes, meridiems =  time_sleeps.sleep_times()
    txt = time_sleeps.message_sleep_now(hours= hours, minutes= minutes, meridiems= meridiems)
    bot.reply_to(message, txt)

#---------------------------------------
# xsmb
# @bot.message_handler(commands=['xsmb'])
# def sign_handler(message):
#     text = xsmb()
#     bot.send_message(message.chat.id, text)
#     xsmb_log.info(text)

# Handles all sent documents and audio files
@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    bot.reply_to(message.chat.id, 'gui file del gi day')


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, 'Tôi không hiểu câu lệnh của bạn.')



# ------------------
# Chạy bot
# ------------------
if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()