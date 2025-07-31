from get_api.xsmb import get_xsmb

from datetime import datetime
def register_handlers(bot):
    @bot.message_handler(commands=['xsmb'])
    def handle_xsmb(message):
        date = '-'.join(map(str, (message.text.split()[1:])))
        if date:
            answer = get_xsmb(date)
        else:  # Nếu không có ngày, lấy kết quả mới nhất, điền ngày hôm nay nếu > 19h hoặc lấy của ngày liên trước
            now = datetime.now()
            if now.hour >= 19:
                date = now.strftime("%d-%m-%Y")
            else:
                # Lấy ngày hôm qua nếu trước 19h vi chua co kết quả
                yesterday = now.replace(day=now.day - 1)
                date = yesterday.strftime("%d-%m-%Y")
            answer = get_xsmb(date)
        bot.send_message(message.chat.id, answer)
        