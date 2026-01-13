import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import schedule
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from get_api.stock import get_stock_info
from logs.logs import setup_logger
from utils.scheduler import start_scheduler

stock_log = setup_logger('stock.log')

# File lưu trữ subscriptions
SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'stock_subscriptions.json')

# Tạo thư mục và file nếu chưa tồn tại
os.makedirs(os.path.dirname(SUBSCRIPTIONS_FILE), exist_ok=True)
if not os.path.exists(SUBSCRIPTIONS_FILE):
    with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)

def load_subscriptions():
    """Đọc danh sách subscriptions từ file JSON"""
    try:
        if os.path.exists(SUBSCRIPTIONS_FILE):
            with open(SUBSCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        stock_log.error(f"Error loading subscriptions: {e}")
        return {}

def save_subscriptions(subscriptions):
    """Lưu subscriptions vào file JSON"""
    try:
        os.makedirs(os.path.dirname(SUBSCRIPTIONS_FILE), exist_ok=True)
        with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(subscriptions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        stock_log.error(f"Error saving subscriptions: {e}")

def format_price(price):
    """Format giá với dấu phẩy phân cách hàng nghìn"""
    if price is None:
        return "N/A"
    return f"{price:,.0f}"

def get_color_indicator(color):
    """Lấy emoji chấm màu theo trạng thái"""
    if color == "green":
        return "🟢"
    elif color == "red":
        return "🔴"
    else:
        return "🟡"

def send_stock_notification(bot):
    """Gửi thông báo giá chứng khoán cho các user đã đăng ký"""
    now = datetime.now()
    
    # Kiểm tra thứ (0=Monday, 6=Sunday)
    if now.weekday() > 4:  # Saturday or Sunday
        return
    
    # Kiểm tra giờ (9h-15h)
    if now.hour < 9 or now.hour >= 15:
        return
    
    subscriptions = load_subscriptions()
    
    for chat_id, symbols in subscriptions.items():
        if not symbols:
            continue
            
        message_parts = ["📊 **CẬP NHẬT GIÁ CHỨNG KHOÁN** 📊\n"]
        
        for symbol in symbols:
            info = get_stock_info(symbol)
            if info:
                current_price = format_price(info['current_price'])
                message_parts.append(
                    f"{get_color_indicator(info['color'])} **{info['symbol']}**: {current_price} VNĐ"
                )
        
        if len(message_parts) > 1:
            try:
                bot.send_message(
                    chat_id=int(chat_id),
                    text="\n".join(message_parts),
                    parse_mode="Markdown"
                )
            except Exception as e:
                stock_log.error(f"Error sending notification to {chat_id}: {e}")

def register_handlers(bot):
    """Đăng ký các handlers cho chức năng stock"""
    
    # Handler 1: Xem giá chứng khoán
    @bot.message_handler(commands=['stock', 'chungkhoan', 'chung', 'ck'])
    def stock_handler(message):
        """Xem giá chứng khoán: /stock VCB"""
        try:
            # Parse command
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(
                    message.chat.id,
                    "❌ Vui lòng nhập mã chứng khoán!\n\n"
                    "📝 Cách dùng: `/stock VCB`",
                    parse_mode="Markdown"
                )
                return
            
            symbol = parts[1].upper()
            info = get_stock_info(symbol)
            
            if not info:
                bot.send_message(
                    message.chat.id,
                    f"❌ Không tìm thấy thông tin cho mã **{symbol}**",
                    parse_mode="Markdown"
                )
                return
            
            # Format thông báo
            color_indicator = get_color_indicator(info['color'])
            change_sign = "+" if info['change_percent'] >= 0 else ""
            
            response = (
                f"📈 **THÔNG TIN CHỨNG KHOÁN** 📈\n\n"
                f"🏢 Mã: **{info['symbol']}**\n"
                f"{color_indicator} Giá hiện tại: **{format_price(info['current_price'])}** VNĐ\n"
                f"📊 Thay đổi: **{change_sign}{info['change_percent']:.2f}%**\n\n"
                f"🔺 Giá trần: {format_price(info['ceiling_price'])} VNĐ\n"
                f"🔻 Giá sàn: {format_price(info['floor_price'])} VNĐ\n"
                f"📌 Giá tham chiếu: {format_price(info['reference_price'])} VNĐ"
            )
            
            bot.send_message(
                message.chat.id,
                response,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            stock_log.error(f"Error in stock_handler: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra, vui lòng thử lại!"
            )
    
    # Handler 2: Quản lý subscriptions
    @bot.message_handler(commands=['stockwatch', 'theodoick', 'ckwatch'])
    def stock_watch_handler(message):
        """Menu quản lý theo dõi chứng khoán"""
        chat_id = str(message.chat.id)
        subscriptions = load_subscriptions()
        current_symbols = subscriptions.get(chat_id, [])
        
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton(
                text="➕ Thêm mã chứng khoán",
                callback_data="stock_add"
            ),
            InlineKeyboardButton(
                text="➖ Xóa mã chứng khoán",
                callback_data="stock_remove"
            ),
            InlineKeyboardButton(
                text="📋 Danh sách đang theo dõi",
                callback_data="stock_list"
            )
        ]
        markup.add(*buttons)
        
        symbols_text = ", ".join(current_symbols) if current_symbols else "Chưa có mã nào"
        
        bot.send_message(
            message.chat.id,
            f"📊 **QUẢN LÝ THEO DÕI CHỨNG KHOÁN** 📊\n\n"
            f"🔔 Nhận thông báo giá mỗi 5 phút\n"
            f"⏰ Thứ 2 - Thứ 6, 9:00 - 15:00\n\n"
            f"📌 Đang theo dõi: **{symbols_text}**",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "stock_add")
    def stock_add_callback(call):
        """Yêu cầu người dùng nhập mã cần thêm"""
        msg = bot.send_message(
            call.message.chat.id,
            "📝 Nhập mã chứng khoán cần theo dõi\n\n"
            "💡 Có thể nhập nhiều mã cách nhau bởi dấu cách hoặc phẩy\n"
            "VD: `VCB HPG FPT` hoặc `VCB, HPG, FPT`",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_add_stock)
        bot.answer_callback_query(call.id)
    
    def process_add_stock(message):
        """Xử lý thêm mã chứng khoán (hỗ trợ nhiều mã cùng lúc)"""
        try:
            # Parse nhiều mã, hỗ trợ cả dấu cách và dấu phẩy
            input_text = message.text.strip().replace(',', ' ')
            symbols = [s.strip().upper() for s in input_text.split() if s.strip()]
            
            if not symbols:
                bot.send_message(
                    message.chat.id,
                    "❌ Vui lòng nhập ít nhất một mã chứng khoán!",
                    parse_mode="Markdown"
                )
                return
            
            chat_id = str(message.chat.id)
            subscriptions = load_subscriptions()
            
            if chat_id not in subscriptions:
                subscriptions[chat_id] = []
            
            # Kiểm tra từng mã
            valid_symbols = []
            invalid_symbols = []
            duplicate_symbols = []
            
            for symbol in symbols:
                # Kiểm tra trùng lặp
                if symbol in subscriptions[chat_id]:
                    duplicate_symbols.append(symbol)
                    continue
                
                # Kiểm tra mã có hợp lệ không
                info = get_stock_info(symbol)
                if info:
                    valid_symbols.append(symbol)
                    subscriptions[chat_id].append(symbol)
                else:
                    invalid_symbols.append(symbol)
            
            # Lưu nếu có mã hợp lệ
            if valid_symbols:
                save_subscriptions(subscriptions)
            
            # Tạo thông báo kết quả
            result_parts = []
            
            if valid_symbols:
                result_parts.append(
                    f"✅ Đã thêm {len(valid_symbols)} mã:\n"
                    f"**{', '.join(valid_symbols)}**"
                )
            
            if duplicate_symbols:
                result_parts.append(
                    f"ℹ️ Đã có trong danh sách ({len(duplicate_symbols)} mã):\n"
                    f"`{', '.join(duplicate_symbols)}`"
                )
            
            if invalid_symbols:
                result_parts.append(
                    f"❌ Không tìm thấy ({len(invalid_symbols)} mã):\n"
                    f"`{', '.join(invalid_symbols)}`"
                )
            
            result_parts.append(f"\n📋 Tổng số mã đang theo dõi: **{len(subscriptions[chat_id])}**")
            
            bot.send_message(
                message.chat.id,
                "\n\n".join(result_parts),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            stock_log.error(f"Error in process_add_stock: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra, vui lòng thử lại!"
            )
    
    @bot.callback_query_handler(func=lambda call: call.data == "stock_remove")
    def stock_remove_callback(call):
        """Hiển thị danh sách để xóa"""
        chat_id = str(call.message.chat.id)
        subscriptions = load_subscriptions()
        current_symbols = subscriptions.get(chat_id, [])
        
        if not current_symbols:
            bot.answer_callback_query(call.id, "Chưa có mã nào để xóa!")
            return
        
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton(
                text=f"❌ {symbol}",
                callback_data=f"stock_del_{symbol}"
            ) for symbol in current_symbols
        ]
        markup.add(*buttons)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🗑️ Chọn mã cần xóa:",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("stock_del_"))
    def stock_delete_callback(call):
        """Xử lý xóa mã"""
        symbol = call.data.replace("stock_del_", "")
        chat_id = str(call.message.chat.id)
        
        subscriptions = load_subscriptions()
        
        if chat_id in subscriptions and symbol in subscriptions[chat_id]:
            subscriptions[chat_id].remove(symbol)
            save_subscriptions(subscriptions)
            
            remaining = subscriptions[chat_id]
            symbols_text = ", ".join(remaining) if remaining else "Chưa có mã nào"
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Đã xóa mã **{symbol}**!\n\n"
                     f"📋 Danh sách còn lại: **{symbols_text}**",
                parse_mode="Markdown"
            )
        
        bot.answer_callback_query(call.id, f"Đã xóa {symbol}")
    
    @bot.callback_query_handler(func=lambda call: call.data == "stock_list")
    def stock_list_callback(call):
        """Hiển thị danh sách đang theo dõi"""
        chat_id = str(call.message.chat.id)
        subscriptions = load_subscriptions()
        current_symbols = subscriptions.get(chat_id, [])
        
        if not current_symbols:
            bot.answer_callback_query(call.id, "Chưa có mã nào!")
            return
        
        message_parts = ["📋 **DANH SÁCH ĐANG THEO DÕI** 📋\n"]
        
        for symbol in current_symbols:
            info = get_stock_info(symbol)
            if info:
                current_price = format_price(info['current_price'])
                change_sign = "+" if info['change_percent'] >= 0 else ""
                message_parts.append(
                    f"{get_color_indicator(info['color'])} **{symbol}**: "
                    f"{current_price} VNĐ ({change_sign}{info['change_percent']:.2f}%)"
                )
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="\n".join(message_parts),
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)
    
    # Đăng ký scheduler để gửi thông báo mỗi 5 phút
    schedule.every(5).minutes.do(send_stock_notification, bot=bot)
    
    # Khởi động scheduler
    start_scheduler()
    
    stock_log.info("Stock handlers registered successfully")
