# -*- coding: utf-8 -*-

import requests
import telebot
import config
from get_api.get_horoscpoe import get_daily_horoscope

# BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_TOKEN = config.BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


def fetch_horoscope(message, sign):
    day = message.text
    horoscope = get_daily_horoscope(sign, day)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:* {data["horoscope_data"]}\n*Sign:* {sign}\n*Day:* {data["date"]}'
    bot.send_message(message.chat.id, "Here's your horoscope!")
    bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")

