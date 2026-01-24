import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import  time_sleeps
from utils.log_helper import log_user_action

def register_handlers(bot):
    @bot.message_handler(commands=['sleep'])
    def handle_time_sleep(message):
        log_user_action(message, "/sleep", "User requested sleep time calculation")
        hours, minutes, meridiems =  time_sleeps.sleep_times()
        txt = time_sleeps.message_sleep_now(hours= hours, minutes= minutes, meridiems= meridiems)
        bot.reply_to(message, txt)
        