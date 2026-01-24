import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.aug import get_gold, URL_SJC, URL_DOJI
import schedule
from utils.scheduler import start_scheduler
import config

def format_gold_message(gold_data, company_name):
    """Format gold price data into a message"""
    message = f"💰 *Giá vàng {company_name}*\n"
    message += f"Cập nhật: {gold_data.get('cap_nhat', 'N/A')}\n\n"
    message += f"📊 *Vàng miếng:*\n"
    message += f"  • Mua vào: {gold_data['vang_mieng']['mua']}\n"
    message += f"  • Bán ra: {gold_data['vang_mieng']['ban']}\n\n"
    message += f"💍 *Vàng nhẫn:*\n"
    message += f"  • Mua vào: {gold_data['vang_nhan']['mua']}\n"
    message += f"  • Bán ra: {gold_data['vang_nhan']['ban']}"
    return message

def send_gold_price(bot, chat_id, url, company_name):
    """Send gold price to a chat"""
    try:
        gold_data = get_gold(url)
        message = format_gold_message(gold_data, company_name)
        bot.send_message(chat_id, message, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Lỗi khi lấy giá vàng {company_name}: {str(e)}")

def send_scheduled_gold_prices(bot):
    """Send both SJC and DOJI prices to scheduled chat IDs"""
    for chat_id in config.SCHEDULE_AUG_CHAT_IDS:
        try:
            # Send SJC price
            gold_sjc = get_gold(URL_SJC)
            message_sjc = format_gold_message(gold_sjc, "SJC")
            bot.send_message(chat_id, message_sjc, parse_mode="Markdown")
            
            # Send DOJI price
            gold_doji = get_gold(URL_DOJI)
            message_doji = format_gold_message(gold_doji, "DOJI")
            bot.send_message(chat_id, message_doji, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending scheduled gold prices to {chat_id}: {str(e)}")

def register_handlers(bot):
    @bot.message_handler(commands=['aug'])
    def handle_aug(message):
        # Parse the command arguments
        args = message.text.split()
        
        if len(args) == 1:
            # /aug - send both SJC and DOJI
            send_gold_price(bot, message.chat.id, URL_SJC, "SJC")
            send_gold_price(bot, message.chat.id, URL_DOJI, "DOJI")
        elif len(args) == 2:
            if args[1].lower() == 'sjc':
                # /aug sjc
                send_gold_price(bot, message.chat.id, URL_SJC, "SJC")
            elif args[1].lower() == 'doji':
                # /aug doji
                send_gold_price(bot, message.chat.id, URL_DOJI, "DOJI")
            else:
                bot.reply_to(message, "❌ Lệnh không hợp lệ. Sử dụng: /aug, /aug sjc, hoặc /aug doji")
        else:
            bot.reply_to(message, "❌ Lệnh không hợp lệ. Sử dụng: /aug, /aug sjc, hoặc /aug doji")
    
    # Setup scheduled task at 9:15 AM
    if config.SCHEDULE_AUG_CHAT_IDS:
        schedule.every().day.at("09:15").do(lambda: send_scheduled_gold_prices(bot))
        start_scheduler()
        print("Scheduled gold price update at 9:15 AM daily")
