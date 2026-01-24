import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.get_answer_simsimi import get_answer_simsimi
from utils.log_helper import log_user_action

def register_handlers(bot):
    @bot.message_handler(commands=['sim', 'simsimi'])
    def handle_simsimi(message):
        quess = ' '.join(map(str, (message.text.split()[1:])))
        log_user_action(message, "/simsimi", f"Question: {quess}")
        answer = get_answer_simsimi(quess)
        bot.send_message(message.chat.id, answer.json()['message'])