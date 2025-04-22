from get_api.catfact import get_cat_fact

def register_handlers(bot):
    @bot.message_handler(commands=['catfact'])
    def handle_start(message):
        txt = get_cat_fact()
        bot.reply_to(message, txt)
