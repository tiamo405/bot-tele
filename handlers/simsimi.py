from get_api.get_answer_simsimi import get_answer_simsimi

def register_handlers(bot):
    @bot.message_handler(commands=['sim', 'simsimi'])
    def handle_simsimi(message):
        quess = ' '.join(map(str, (message.text.split()[1:])))
        answer = get_answer_simsimi(quess)
        bot.send_message(message.chat.id, answer.json()['message'])