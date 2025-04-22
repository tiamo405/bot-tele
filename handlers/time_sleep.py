from utils import  time_sleeps
def register_handlers(bot):
    @bot.message_handler(commands=['sleep'])
    def handle_time_sleep(message):
        hours, minutes, meridiems =  time_sleeps.sleep_times()
        txt = time_sleeps.message_sleep_now(hours= hours, minutes= minutes, meridiems= meridiems)
        bot.reply_to(message, txt)
        