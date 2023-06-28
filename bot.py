# -*- coding: utf-8 -*-

import os
import telebot
import config
from utils import horoscope, time_sleeps
from get_api.get_answer_simsimi import get_answer_simsimi
from logs.logs import setup_logger 

# logger = setup_logger('logs.log')
simsimi_log = setup_logger("simsimi.log")
# tuvi_log = setup_logger('tuvi.log')

BOT_TOKEN = config.BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello, how are you doing?")

#-------------------------
# xem bói tử vi cung hoàng đạo  + ngày
@bot.message_handler(commands=['horoscope', 'tuvi'])
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


# Handles all sent documents and audio files
@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    bot.reply_to(message.chat.id, 'gui file del gi day')


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, 'Tôi không hiểu câu lệnh của bạn.')

# def main():
bot.infinity_polling()

# if __name__ == "__main__" :
#     main()