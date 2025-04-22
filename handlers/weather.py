import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.weather import get_weather

def register_handlers(bot):
    @bot.message_handler(commands=['weather'])
    def handle_start(message):
        weather = get_weather()
        country = weather["country_code"]
        city = weather["city_name"]
        temp = weather["temp"]
        api = weather["aqi"]
        txt = "Thời tiết tại {city}, {country} hiện tại: {temp}°C\nChất lượng không khí: {api}".format(city=city, country=country, temp=temp, api=api)
        bot.reply_to(message, txt)
