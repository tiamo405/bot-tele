# -*- coding: utf-8 -*-

import os
import telebot
import config
from horoscope import fetch_horoscope
from get_api.get_answer_simsimi import get_answer_simsimi

# BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_TOKEN = config.BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello, how are you doing?")

# xem bói tử vi cung hoàng đạo  + ngày
@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = "What's your zodiac sign?\nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, *Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)

def day_handler(message):
    sign = message.text
    text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, fetch_horoscope, sign.capitalize())
#----------------------------
# chat voi simsimi
@bot.message_handler(commands=['simsimi', 'sim'])
def start_simsimi(message) :
    quess = ' '.join(map(str, (message.text.split()[1:])))
    answer = get_answer_simsimi(quess)
    bot.send_message(message.chat.id, answer.json()['message'])
    print(quess)

@bot.callback_query_handler(func=lambda call: True)
def chat_simsimi(message) :
    bot.reply_to(message, "chưa cập nhật bot simsimi")

#


# Handles all sent documents and audio files
@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    bot.reply_to(message.chat.id, 'gui file del gi day')


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, 'Tôi không hiểu câu lệnh của bạn.')

bot.infinity_polling()