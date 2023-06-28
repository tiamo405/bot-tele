# -*- coding: utf-8 -*-

import requests
import telebot
import config
from get_api.get_horoscpoe import get_daily_horoscope
from logs.logs import setup_logger 
import logging

logger = setup_logger('logs.log')

tuvi_log = setup_logger('tuvi.log')

BOT_TOKEN = config.BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)


def fetch_horoscope(message, sign):
    day = message.text
    try:
        horoscope = get_daily_horoscope(sign, day)
        data = horoscope["data"]
        horoscope_message = f'*Horoscope:* {data["horoscope_data"]}\n*Sign:* {sign}\n*Day:* {data["date"]}'
        bot.send_message(message.chat.id, "Here's your horoscope!")
        bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")
        tuvi_log.info('sign : {}, day : {}, \n predict : {}'.format(sign, day, horoscope_message))
    except :
        bot.send_message(message.chat.id, "Đã xảy ra lỗi, xin thử lại.\n An error has occurred. Please try again.")
        tuvi_log.info('sign : {}, day : {}, \n predict : Đã xảy ra lỗi, xin thử lại.\n An error has occurred. Please try again.'.format(sign, day))

