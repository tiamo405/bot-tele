# -*- coding: utf-8 -*-

import os
import telebot
import config
from horoscope import day_handler


# BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_TOKEN = config.BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Nam, how are you doing?")


@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = "What's your zodiac sign?\nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, *Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)



# Handles all sent documents and audio files
@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    bot.reply_to(message.chat.id, 'gui file del gi day')


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, 'gi day bro')
    bot.send_message(message.chat.id, 'noi gi tiep di')

bot.infinity_polling()