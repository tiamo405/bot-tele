import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.usd import get_vcb_exchange_rate
from utils.log_helper import log_user_action
from logs.logs import setup_logger
from utils.retry_decorator import retry_on_exception
from utils.json_storage import JSONStorage
from datetime import datetime
from config import DATA_DIR

exchange_log = setup_logger('exchange_rate.log')

# Initialize exchange rate storage
EXCHANGE_RATE_FILE = os.path.join(DATA_DIR, 'exchange_rates.json')
exchange_storage = JSONStorage(EXCHANGE_RATE_FILE, default_data={})

@retry_on_exception(max_retries=3, delay=1)
def get_exchange_rate_with_retry(currency_code):
    """Get exchange rate with retry logic"""
    return get_vcb_exchange_rate(currency_code)

def get_previous_rate(currency):
    """
    Get the most recent saved exchange rate for comparison
    
    Args:
        currency: Currency code (e.g., 'USD')
    
    Returns:
        Dict with buy/sell prices or None if no history
    """
    try:
        all_rates = exchange_storage.load()
        
        if currency in all_rates and len(all_rates[currency]) > 0:
            # Return the most recent entry
            latest = all_rates[currency][0]
            return {
                "buy": latest.get("buy"),
                "sell": latest.get("sell")
            }
        return None
    except Exception as e:
        exchange_log.error(f"Error getting previous rate for {currency}: {str(e)}")
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

def save_exchange_rate(rate_data):
    """
    Save exchange rate data to history file
    
    Args:
        rate_data: Dict with keys: currency, buy, sell, source
    """
    try:
        # Load current data
        all_rates = exchange_storage.load()
        
        currency = rate_data['currency']
        
        # Initialize currency list if not exists
        if currency not in all_rates:
            all_rates[currency] = []
        
        # Create new entry with timestamp
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "buy": rate_data['buy'],
            "sell": rate_data['sell'],
            "source": rate_data['source']
        }
        
        # Add to history (newest first)
        all_rates[currency].insert(0, new_entry)
        
        # Keep only last 100 entries per currency to avoid file bloat
        all_rates[currency] = all_rates[currency][:100]
        
        # Save back to file
        exchange_storage.save(all_rates)
        exchange_log.info(f"Saved exchange rate: {currency} | Buy: {rate_data['buy']} | Sell: {rate_data['sell']}")
        
    except Exception as e:
        exchange_log.error(f"Error saving exchange rate {rate_data['currency']}: {str(e)}")

def register_handlers(bot):
    @bot.message_handler(commands=['tigia'])
    def handle_exchange_rate(message):
        """Handle /tigia command to get VCB exchange rates"""
        args = message.text.split()
        
        # Default to USD if no currency specified
        if len(args) == 1:
            currency = "USD"
        elif len(args) == 2:
            currency = args[1].upper()
        else:
            bot.reply_to(message, "❌ Lệnh không hợp lệ. Sử dụng: /tigia hoặc /tigia USD")
            return
        
        log_user_action(message, "/tigia", f"Requested exchange rate: {currency}")
        exchange_log.info(f"Exchange rate request: {currency} | User: {message.from_user.username} (ID: {message.from_user.id})")
        
        try:
            rate_data = get_exchange_rate_with_retry(currency)
            
            if rate_data is None:
                bot.send_message(message.chat.id, f"❌ Không tìm thấy tỷ giá cho {currency}")
                exchange_log.warning(f"Exchange rate not found: {currency} | Chat: {message.chat.id}")
                return
            
            # Get previous rate BEFORE saving new one
            previous_rate = get_previous_rate(currency)
            
            # Save exchange rate to history
            save_exchange_rate(rate_data)
            
            # Determine price indicators
            buy_indicator = get_price_indicator(
                rate_data['buy'], 
                previous_rate['buy'] if previous_rate else None
            )
            sell_indicator = get_price_indicator(
                rate_data['sell'], 
                previous_rate['sell'] if previous_rate else None
            )
            
            # Format the message
            msg = f"💱 *Tỷ giá {rate_data['currency']}*\n\n"
            
            if rate_data['buy'] is not None:
                msg += f"{buy_indicator} Mua vào: *{rate_data['buy']:,.0f} VND*\n"
            else:
                msg += f"⚪ Mua vào: *-*\n"
            
            if rate_data['sell'] is not None:
                msg += f"{sell_indicator} Bán ra: *{rate_data['sell']:,.0f} VND*\n"
            else:
                msg += f"⚪ Bán ra: *-*\n"
            
            msg += f"\n_Nguồn: {rate_data['source']}_"
            
            # Add price change info if there's previous data
            if previous_rate:
                msg += "\n\n📊 _So với lần trước:_"
                if previous_rate['buy'] and rate_data['buy']:
                    buy_change = rate_data['buy'] - previous_rate['buy']
                    if buy_change > 0:
                        msg += f"\n• Mua: +{buy_change:,.0f} VND"
                    elif buy_change < 0:
                        msg += f"\n• Mua: {buy_change:,.0f} VND"
                    else:
                        msg += f"\n• Mua: Không đổi"
                
                if previous_rate['sell'] and rate_data['sell']:
                    sell_change = rate_data['sell'] - previous_rate['sell']
                    if sell_change > 0:
                        msg += f"\n• Bán: +{sell_change:,.0f} VND"
                    elif sell_change < 0:
                        msg += f"\n• Bán: {sell_change:,.0f} VND"
                    else:
                        msg += f"\n• Bán: Không đổi"
            
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
            exchange_log.info(f"Exchange rate sent: {currency} | Buy: {rate_data['buy']} | Sell: {rate_data['sell']} | Chat: {message.chat.id}")
            
        except Exception as e:
            exchange_log.error(f"Error getting exchange rate {currency}: {str(e)}")
            bot.send_message(message.chat.id, f"❌ Lỗi khi lấy tỷ giá {currency}: {str(e)}")
