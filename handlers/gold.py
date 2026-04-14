import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.gold import get_gold, URL_SJC, URL_DOJI, make_gapi_request, make_alpha_request, make_gold_XAUUSD_request
from get_api.usd import get_vcb_exchange_rate
from get_api.usd_black import get_usd_black_rate
from utils.log_helper import log_user_action
from logs.logs import setup_logger
from utils.json_storage import JSONStorage
from datetime import datetime
import schedule
from utils.scheduler import start_scheduler
import config
from utils.notification_registry import get_chat_ids

aug_log = setup_logger('aug.log')

# Initialize gold price storage
GOLD_PRICE_FILE = os.path.join(config.DATA_DIR, 'gold_prices.json')
gold_storage = JSONStorage(GOLD_PRICE_FILE, default_data={})

def extract_price_number(price_str):
    """Extract numeric price from formatted strings like '180.800 x1000đ/lượng' or '180.800'"""
    try:
        # Remove everything after and including 'x1000' or just get the number part
        price_part = price_str.split('x1000')[0].strip()
        # Remove any currency symbols and convert to float
        price_part = price_part.replace(',', '').replace('.', '').strip()
        return float(price_part) / 1000  # Convert to actual thousands
    except:
        return 0

def get_previous_gold_price(gold_type):
    """
    Get the most recent saved gold price for comparison
    
    Args:
        gold_type: Type of gold (e.g., 'SJC_MIENG', 'DOJI_NHAN', 'WORLD_GOLD_USD')
    
    Returns:
        Dict with buy/sell prices or None if no history
    """
    try:
        all_prices = gold_storage.load()
        
        if gold_type in all_prices and len(all_prices[gold_type]) > 0:
            latest = all_prices[gold_type][0]
            return {
                "buy": latest.get("buy"),
                "sell": latest.get("sell")
            }
        return None
    except Exception as e:
        aug_log.error(f"Error getting previous gold price for {gold_type}: {str(e)}")
        return None

def get_price_indicator(current, previous):
    """
    Get color indicator based on price change
    
    Args:
        current: Current price (float or None)
        previous: Previous price (float or None)
    
    Returns:
        Emoji indicator: 🟢 (up), 🔴 (down), 🟡 (same)
    """
    if current is None or previous is None:
        return "⚪"  # White circle for no data
    
    if current > previous:
        return "🟢"  # Green - price increased
    elif current < previous:
        return "🔴"  # Red - price decreased
    else:
        return "🟡"  # Yellow - price unchanged

def save_gold_price(gold_type, buy_price, sell_price):
    """
    Save gold price data to history file
    
    Args:
        gold_type: Type of gold (e.g., 'SJC_MIENG', 'DOJI_NHAN')
        buy_price: Buy price (float)
        sell_price: Sell price (float)
    """
    try:
        all_prices = gold_storage.load()
        
        # Initialize gold type list if not exists
        if gold_type not in all_prices:
            all_prices[gold_type] = []
        
        # Create new entry with timestamp
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "buy": buy_price,
            "sell": sell_price
        }
        
        # Add to history (newest first)
        all_prices[gold_type].insert(0, new_entry)
        
        # Keep only last 100 entries per type to avoid file bloat
        all_prices[gold_type] = all_prices[gold_type][:100]
        
        # Save back to file
        gold_storage.save(all_prices)
        aug_log.info(f"Saved gold price: {gold_type} | Buy: {buy_price} | Sell: {sell_price}")
        
    except Exception as e:
        aug_log.error(f"Error saving gold price {gold_type}: {str(e)}")

def get_world_gold_price_vnd():
    """Get world gold price in VND converted by bank and black-market USD rates"""
    try:
        # Get world gold price in USD/oz
        price_usd = float(make_alpha_request())
        origin = "AlphaVantage"
        if not price_usd:
            price_usd = float(make_gapi_request())
            origin = "GoldAPI.io"
        if not price_usd:
            price_usd = float(make_gold_XAUUSD_request())
            origin = "vang.today"
        
        if not price_usd:
            return None

        # Get USD exchange rates
        bank_rate_data = get_vcb_exchange_rate("USD")
        bank_sell = bank_rate_data.get('sell') if bank_rate_data else None

        black_sell = None
        try:
            black_rate_data = get_usd_black_rate()
            black_sell = black_rate_data.get('sell') if black_rate_data else None
        except Exception as black_error:
            aug_log.warning(f"Could not fetch black-market USD rate: {str(black_error)}")

        if bank_sell is None and black_sell is None:
            return None

        # Convert USD/oz to VND/lượng (1 oz = 31.1035 grams, 1 lượng = 37.5 grams)
        oz_to_luong = 37.5 / 31.1035
        price_vnd_bank = price_usd * bank_sell * oz_to_luong if bank_sell is not None else None
        price_vnd_black = price_usd * black_sell * oz_to_luong if black_sell is not None else None

        return {
            'price_usd': price_usd,
            'exchange_rate_bank': bank_sell,
            'exchange_rate_black': black_sell,
            'price_vnd_bank': price_vnd_bank,
            'price_vnd_black': price_vnd_black,
            'origin': origin
        }
    except Exception as e:
        aug_log.error(f"Error calculating world gold price: {str(e)}")
        return None

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
        aug_log.info(f"Gold price sent: {company_name} | Buy: {gold_data['vang_mieng']['mua']} | Sell: {gold_data['vang_mieng']['ban']} | Chat: {chat_id}")
    except Exception as e:
        aug_log.error(f"Error sending gold price {company_name} to {chat_id}: {str(e)}")
        bot.send_message(chat_id, f"❌ Lỗi khi lấy giá vàng {company_name}: {str(e)}")

def send_scheduled_gold_prices(bot):
    """Send simplified gold prices to scheduled chat IDs"""
    aug_log.info(f"Scheduled gold price update started at 9:00 AM")
    for chat_id in get_chat_ids("schedule_aug"):
        try:
            # Get SJC and DOJI prices
            gold_sjc = get_gold(URL_SJC)
            gold_doji = get_gold(URL_DOJI)
            
            # Extract numeric prices
            sjc_buy = extract_price_number(gold_sjc['vang_mieng']['mua'])
            sjc_sell = extract_price_number(gold_sjc['vang_mieng']['ban'])
            doji_buy = extract_price_number(gold_doji['vang_nhan']['mua'])
            doji_sell = extract_price_number(gold_doji['vang_nhan']['ban'])
            
            # Get world gold price in VND
            world_price = get_world_gold_price_vnd()
            
            msg = ""
            if world_price:
                msg += f"🌏 Giá TG: {world_price['price_usd']:,.2f} USD/oz\n"
                msg += f"  (Nguồn: {world_price['origin']})\n"

                if world_price['exchange_rate_bank'] is not None and world_price['price_vnd_bank'] is not None:
                    diff_bank = (sjc_sell * 1_000_000) - world_price['price_vnd_bank']
                    diff_bank_icon = "📈" if diff_bank > 0 else "📉"
                    msg += f"🏦 Tỷ giá bank: {world_price['exchange_rate_bank']:,.0f} → Giá quy đổi: {world_price['price_vnd_bank']:,.0f} VND\n"
                    msg += f"🏅 Chênh lệch SJC (bank): {diff_bank_icon} {abs(diff_bank):,.0f} VND\n"

                if world_price['exchange_rate_black'] is not None and world_price['price_vnd_black'] is not None:
                    diff_black = (sjc_sell * 1_000_000) - world_price['price_vnd_black']
                    diff_black_icon = "📈" if diff_black > 0 else "📉"
                    msg += f"🏴 Tỷ giá chợ đen: {world_price['exchange_rate_black']:,.0f} → Giá quy đổi: {world_price['price_vnd_black']:,.0f} VND\n"
                    msg += f"🏅 Chênh lệch SJC (chợ đen): {diff_black_icon} {abs(diff_black):,.0f} VND\n"

                if world_price['price_vnd_bank'] is not None and world_price['price_vnd_black'] is not None:
                    spread = world_price['price_vnd_black'] - world_price['price_vnd_bank']
                    spread_icon = "📈" if spread > 0 else ("📉" if spread < 0 else "🟰")
                    msg += f"🔁 Chợ đen - bank: {spread_icon} {spread:,.0f} VND\n"

                msg += "\n"
            
            msg += "━━━━━━━━━━━━━━━━\n"
            msg += f"👑 Miếng SJC: {sjc_buy:,.3f} - {sjc_sell:,.3f}\n"
            msg += f"⚜️ Doji: {doji_buy:,.3f} - {doji_sell:,.3f}"
            
            bot.send_message(chat_id, msg)
            aug_log.info(f"Scheduled gold prices sent successfully to chat {chat_id}")
        except Exception as e:
            aug_log.error(f"Error sending scheduled gold prices to {chat_id}: {str(e)}")

def register_handlers(bot):
    @bot.message_handler(commands=['vang', 'giavang'])
    def handle_aug(message):
        """Handle /vang and /giavang command with world price comparison"""
        command_used = message.text.split()[0].lower() if message.text else "/vang"
        log_user_action(message, command_used, "Requested gold price with comparison")
        aug_log.info(f"Gold price request | User: {message.from_user.username} (ID: {message.from_user.id})")
        
        try:
            # Get SJC and DOJI prices
            gold_sjc = get_gold(URL_SJC)
            gold_doji = get_gold(URL_DOJI)
            
            # Extract numeric prices
            sjc_buy = extract_price_number(gold_sjc['vang_mieng']['mua'])
            sjc_sell = extract_price_number(gold_sjc['vang_mieng']['ban'])
            doji_buy = extract_price_number(gold_doji['vang_nhan']['mua'])
            doji_sell = extract_price_number(gold_doji['vang_nhan']['ban'])
            
            # Get previous prices BEFORE saving new ones
            prev_sjc = get_previous_gold_price('SJC_MIENG')
            prev_doji = get_previous_gold_price('DOJI_NHAN')
            
            # Save new prices to history
            save_gold_price('SJC_MIENG', sjc_buy, sjc_sell)
            save_gold_price('DOJI_NHAN', doji_buy, doji_sell)
            
            # Get price indicators
            sjc_buy_indicator = get_price_indicator(sjc_buy, prev_sjc['buy'] if prev_sjc else None)
            sjc_sell_indicator = get_price_indicator(sjc_sell, prev_sjc['sell'] if prev_sjc else None)
            doji_buy_indicator = get_price_indicator(doji_buy, prev_doji['buy'] if prev_doji else None)
            doji_sell_indicator = get_price_indicator(doji_sell, prev_doji['sell'] if prev_doji else None)
            
            # Get world gold price in VND
            world_price = get_world_gold_price_vnd()
            
            msg = ""
            if world_price:
                msg += f"🌏 Giá TG: {world_price['price_usd']:,.2f} USD/oz\n"
                msg += f"  (Nguồn: {world_price['origin']})\n"

                if world_price['exchange_rate_bank'] is not None and world_price['price_vnd_bank'] is not None:
                    diff_bank = (sjc_sell * 1_000_000) - world_price['price_vnd_bank']
                    diff_bank_icon = "📈" if diff_bank > 0 else "📉"
                    msg += f"🏦 Tỷ giá bank: {world_price['exchange_rate_bank']:,.0f} → Giá quy đổi: {world_price['price_vnd_bank']:,.0f} VND\n"
                    msg += f"🏅 Chênh lệch SJC (bank): {diff_bank_icon} {abs(diff_bank):,.0f} VND\n"

                if world_price['exchange_rate_black'] is not None and world_price['price_vnd_black'] is not None:
                    diff_black = (sjc_sell * 1_000_000) - world_price['price_vnd_black']
                    diff_black_icon = "📈" if diff_black > 0 else "📉"
                    msg += f"🏴 Tỷ giá chợ đen: {world_price['exchange_rate_black']:,.0f} → Giá quy đổi: {world_price['price_vnd_black']:,.0f} VND\n"
                    msg += f"🏅 Chênh lệch SJC (chợ đen): {diff_black_icon} {abs(diff_black):,.0f} VND\n"

                if world_price['price_vnd_bank'] is not None and world_price['price_vnd_black'] is not None:
                    spread = world_price['price_vnd_black'] - world_price['price_vnd_bank']
                    spread_icon = "📈" if spread > 0 else ("📉" if spread < 0 else "🟰")
                    msg += f"🔁 Chợ đen - bank: {spread_icon} {spread:,.0f} VND\n"

                msg += "\n"
            
            msg += "━━━━━━━━━━━━━━━━\n"
            msg += f"👑 Miếng SJC: {sjc_buy_indicator} {sjc_buy:,.3f} - {sjc_sell_indicator} {sjc_sell:,.3f}\n"
            msg += f"⚜️ Doji: {doji_buy_indicator} {doji_buy:,.3f} - {doji_sell_indicator} {doji_sell:,.3f}"
            
            # Add price change info if there's previous data
            if prev_sjc or prev_doji:
                msg += "\n\n📊 _So với lần trước:_"
                
                if prev_sjc:
                    sjc_buy_change = sjc_buy - prev_sjc['buy']
                    sjc_sell_change = sjc_sell - prev_sjc['sell']
                    msg += f"\n👑 SJC:"
                    if sjc_buy_change != 0:
                        msg += f" Mua {'+' if sjc_buy_change > 0 else ''}{sjc_buy_change:,.3f}"
                    if sjc_sell_change != 0:
                        msg += f" | Bán {'+' if sjc_sell_change > 0 else ''}{sjc_sell_change:,.3f}"
                    if sjc_buy_change == 0 and sjc_sell_change == 0:
                        msg += " Không đổi"
                
                if prev_doji:
                    doji_buy_change = doji_buy - prev_doji['buy']
                    doji_sell_change = doji_sell - prev_doji['sell']
                    msg += f"\n⚜️ Doji:"
                    if doji_buy_change != 0:
                        msg += f" Mua {'+' if doji_buy_change > 0 else ''}{doji_buy_change:,.3f}"
                    if doji_sell_change != 0:
                        msg += f" | Bán {'+' if doji_sell_change > 0 else ''}{doji_sell_change:,.3f}"
                    if doji_buy_change == 0 and doji_sell_change == 0:
                        msg += " Không đổi"
            
            bot.send_message(message.chat.id, msg)
            aug_log.info(f"Gold prices sent with comparison | Chat: {message.chat.id}")
            
        except Exception as e:
            aug_log.error(f"Error getting gold prices: {str(e)}")
            bot.send_message(message.chat.id, f"❌ Lỗi khi lấy giá vàng: {str(e)}")
    
    @bot.message_handler(commands=['vangsjc'])
    def handle_aug_sjc(message):
        """Handle /vangsjc command for detailed SJC price"""
        log_user_action(message, "/vangsjc", "Requested SJC gold price")
        aug_log.info(f"SJC gold price request | User: {message.from_user.username} (ID: {message.from_user.id})")
        send_gold_price(bot, message.chat.id, URL_SJC, "SJC")
    
    @bot.message_handler(commands=['vangdoji'])
    def handle_aug_doji(message):
        """Handle /vangdoji command for detailed DOJI price"""
        log_user_action(message, "/vangdoji", "Requested DOJI gold price")
        aug_log.info(f"DOJI gold price request | User: {message.from_user.username} (ID: {message.from_user.id})")
        send_gold_price(bot, message.chat.id, URL_DOJI, "DOJI")
    
    @bot.message_handler(commands=['vangtg'])
    def handle_world_gold(message):
        """Handle /vangtg command to get world gold price"""
        log_user_action(message, "/vangtg", "Requested world gold price")
        aug_log.info(f"World gold price request | User: {message.from_user.username} (ID: {message.from_user.id})")
        
        try:
            price_usd = make_gold_XAUUSD_request()
            if not price_usd:
                price_usd = make_gapi_request()
            if not price_usd:
                price_usd = make_alpha_request()
            
            if price_usd:
                # Get previous price BEFORE saving
                prev_world = get_previous_gold_price('WORLD_GOLD_USD')
                
                # Save new price (using same value for buy and sell since world price is single value)
                save_gold_price('WORLD_GOLD_USD', price_usd, price_usd)
                
                # Get price indicator
                price_indicator = get_price_indicator(
                    price_usd,
                    prev_world['buy'] if prev_world else None
                )
                
                msg = f"🌐 *Giá vàng thế giới*\n\n"
                msg += f"💵 Giá: {price_indicator} *${price_usd:,.2f}/oz*\n"
                
                # Add comparison if there's previous data
                if prev_world and prev_world['buy']:
                    price_change = price_usd - prev_world['buy']
                    msg += f"\n📊 _So với lần trước:_"
                    if price_change > 0:
                        msg += f"\n• +${price_change:,.2f}/oz"
                    elif price_change < 0:
                        msg += f"\n• ${price_change:,.2f}/oz"
                    else:
                        msg += f"\n• Không đổi"
                
                msg += f"\n\n_Nguồn: GoldAPI.io_"
                
                bot.send_message(message.chat.id, msg, parse_mode="Markdown")
                aug_log.info(f"World gold price sent: ${price_usd}/oz | Chat: {message.chat.id}")
            else:
                bot.send_message(message.chat.id, "❌ Không thể lấy giá vàng thế giới lúc này. Vui lòng thử lại sau.")
                aug_log.warning(f"Failed to get world gold price | Chat: {message.chat.id}")
        except Exception as e:
            aug_log.error(f"Error getting world gold price: {str(e)}")
            bot.send_message(message.chat.id, f"❌ Lỗi khi lấy giá vàng thế giới: {str(e)}")
    
    # Setup scheduled task at 9:00 AM
    if get_chat_ids("schedule_aug"):
        schedule.every().day.at("09:00").do(lambda: send_scheduled_gold_prices(bot))
        start_scheduler()
        print("Scheduled gold price update at 9:00 AM daily")