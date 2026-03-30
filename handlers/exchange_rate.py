import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_api.usd import get_vcb_exchange_rate
from get_api.usd_black import get_usd_black_rate
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
HISTORY_LIMIT = 100


def build_history_key(currency, market):
    return f"{currency.upper()}_{market.upper()}"

@retry_on_exception(max_retries=3, delay=1)
def get_bank_exchange_rate_with_retry(currency_code):
    """Get exchange rate with retry logic"""
    return get_vcb_exchange_rate(currency_code)


@retry_on_exception(max_retries=3, delay=1)
def get_black_exchange_rate_with_retry():
    """Get USD black-market exchange rate with retry logic"""
    return get_usd_black_rate()

def get_previous_rate(currency, market):
    """
    Get the most recent saved exchange rate for comparison
    
    Args:
        currency: Currency code (e.g., 'USD')
    
    Returns:
        Dict with buy/sell prices or None if no history
    """
    try:
        all_rates = exchange_storage.load()
        history_key = build_history_key(currency, market)

        if history_key in all_rates and len(all_rates[history_key]) > 0:
            latest = all_rates[history_key][0]
            return {
                "buy": latest.get("buy"),
                "sell": latest.get("sell")
            }

        if market.upper() == "BANK" and currency.upper() in all_rates and len(all_rates[currency.upper()]) > 0:
            latest = all_rates[currency.upper()][0]
            return {
                "buy": latest.get("buy"),
                "sell": latest.get("sell")
            }

        return None
    except Exception as e:
        exchange_log.error(f"Error getting previous rate for {currency}/{market}: {str(e)}")
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

def save_exchange_rate(rate_data, market):
    """
    Save exchange rate data to history file
    
    Args:
        rate_data: Dict with keys: currency, buy, sell, source
    """
    try:
        # Load current data
        all_rates = exchange_storage.load()
        
        history_key = build_history_key(rate_data['currency'], market)
        
        # Initialize currency list if not exists
        if history_key not in all_rates:
            all_rates[history_key] = []
        
        # Create new entry with timestamp
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "buy": rate_data['buy'],
            "sell": rate_data['sell'],
            "source": rate_data.get('source')
        }
        
        # Add to history (newest first)
        all_rates[history_key].insert(0, new_entry)
        
        # Keep only last N entries per currency/market to avoid file bloat
        all_rates[history_key] = all_rates[history_key][:HISTORY_LIMIT]
        
        # Save back to file
        exchange_storage.save(all_rates)
        exchange_log.info(f"Saved exchange rate: {history_key} | Buy: {rate_data['buy']} | Sell: {rate_data['sell']}")
        
    except Exception as e:
        exchange_log.error(f"Error saving exchange rate {rate_data['currency']}: {str(e)}")


def format_change(current, previous):
    if current is None or previous is None:
        return None

    diff = current - previous
    if diff > 0:
        return f"+{diff:,.0f} VND"
    if diff < 0:
        return f"{diff:,.0f} VND"
    return "Không đổi"

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
            bank_rate = get_bank_exchange_rate_with_retry(currency)
            
            if bank_rate is None:
                bot.send_message(message.chat.id, f"❌ Không tìm thấy tỷ giá cho {currency}")
                exchange_log.warning(f"Exchange rate not found: {currency} | Chat: {message.chat.id}")
                return
            
            prev_bank = get_previous_rate(currency, "BANK")
            save_exchange_rate(bank_rate, "BANK")

            bank_buy_indicator = get_price_indicator(
                bank_rate['buy'],
                prev_bank['buy'] if prev_bank else None
            )
            bank_sell_indicator = get_price_indicator(
                bank_rate['sell'],
                prev_bank['sell'] if prev_bank else None
            )

            black_rate = None
            prev_black = None
            black_buy_indicator = "⚪"
            black_sell_indicator = "⚪"

            if currency == "USD":
                try:
                    black_rate = get_black_exchange_rate_with_retry()
                except Exception as black_error:
                    exchange_log.warning(f"Failed to fetch USD black-market rate: {str(black_error)}")

                if black_rate:
                    prev_black = get_previous_rate(currency, "BLACK")
                    save_exchange_rate(black_rate, "BLACK")
                    black_buy_indicator = get_price_indicator(
                        black_rate['buy'],
                        prev_black['buy'] if prev_black else None
                    )
                    black_sell_indicator = get_price_indicator(
                        black_rate['sell'],
                        prev_black['sell'] if prev_black else None
                    )
            
            msg = f"💱 *Tỷ giá {currency}*\n\n"

            msg += "🏦 *Ngân hàng (Vietcombank)*\n"
            if bank_rate['buy'] is not None:
                msg += f"{bank_buy_indicator} Mua vào: *{bank_rate['buy']:,.0f} VND*\n"
            else:
                msg += "⚪ Mua vào: *-*\n"

            if bank_rate['sell'] is not None:
                msg += f"{bank_sell_indicator} Bán ra: *{bank_rate['sell']:,.0f} VND*\n"
            else:
                msg += "⚪ Bán ra: *-*\n"

            msg += "\n"
            if currency == "USD":
                msg += "🏴 *Chợ đen*\n"
                if black_rate:
                    msg += f"{black_buy_indicator} Mua vào: *{black_rate['buy']:,.0f} VND*\n"
                    msg += f"{black_sell_indicator} Bán ra: *{black_rate['sell']:,.0f} VND*\n"
                    spread_buy = black_rate['buy'] - bank_rate['buy'] if bank_rate['buy'] is not None else None
                    spread_sell = black_rate['sell'] - bank_rate['sell'] if bank_rate['sell'] is not None else None
                    msg += "\n🔁 _Chênh lệch chợ đen - bank:_"
                    if spread_buy is not None:
                        msg += f"\n• Mua: {'+' if spread_buy > 0 else ''}{spread_buy:,.0f} VND"
                    if spread_sell is not None:
                        msg += f"\n• Bán: {'+' if spread_sell > 0 else ''}{spread_sell:,.0f} VND"
                else:
                    msg += "⚪ Chưa lấy được dữ liệu chợ đen lúc này\n"
            else:
                msg += "ℹ️ _Giá chợ đen hiện chỉ hỗ trợ USD._\n"

            msg += f"\n_Nguồn: {bank_rate.get('source', 'Vietcombank')} + tygiausd.org_"

            if prev_bank or prev_black:
                msg += "\n\n📊 _So với lần trước:_"

                bank_buy_change = format_change(bank_rate['buy'], prev_bank['buy'] if prev_bank else None)
                bank_sell_change = format_change(bank_rate['sell'], prev_bank['sell'] if prev_bank else None)
                if bank_buy_change or bank_sell_change:
                    msg += "\n🏦 Bank:"
                    if bank_buy_change:
                        msg += f" Mua {bank_buy_change}"
                    if bank_sell_change:
                        msg += f" | Bán {bank_sell_change}"

                if prev_black and black_rate:
                    black_buy_change = format_change(black_rate['buy'], prev_black['buy'])
                    black_sell_change = format_change(black_rate['sell'], prev_black['sell'])
                    if black_buy_change or black_sell_change:
                        msg += "\n🏴 Chợ đen:"
                        if black_buy_change:
                            msg += f" Mua {black_buy_change}"
                        if black_sell_change:
                            msg += f" | Bán {black_sell_change}"
            
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
            exchange_log.info(
                f"Exchange rate sent: {currency} | Bank Buy: {bank_rate['buy']} | Bank Sell: {bank_rate['sell']} | "
                f"Black Buy: {black_rate['buy'] if black_rate else None} | Black Sell: {black_rate['sell'] if black_rate else None} | "
                f"Chat: {message.chat.id}"
            )
            
        except Exception as e:
            exchange_log.error(f"Error getting exchange rate {currency}: {str(e)}")
            bot.send_message(message.chat.id, f"❌ Lỗi khi lấy tỷ giá {currency}: {str(e)}")
