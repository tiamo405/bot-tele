from get_api.xsmb import get_xsmb

def register_handlers(bot):
    @bot.message_handler(commands=['xsmb'])
    def handle_xsmb(message):
        date = ' '.join(map(str, (message.text.split()[1:])))
        if date:
            answer = get_xsmb(date)
        else:
            answer = get_xsmb()
        bot.send_message(message.chat.id, answer)
        