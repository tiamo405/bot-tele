import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.catfact import get_cat_fact
from utils.log_helper import log_user_action

def register_handlers(bot):
    @bot.message_handler(commands=['catfact'])
    def handle_start(message):
        log_user_action(message, "/catfact", "User requested cat fact")
        txt = get_cat_fact()
        bot.reply_to(message, txt)
