import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schedule
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from get_api.stock import get_stock_info, get_stock_info_list_smart
from logs.logs import setup_logger
from utils.scheduler import start_scheduler
from utils.log_helper import log_user_action
from utils.json_storage import JSONStorage
from utils.formatters import format_price, format_percentage, get_stock_color_indicator

stock_log = setup_logger('stock.log')

# File lưu trữ subscriptions - sử dụng JSONStorage
SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'stock_subscriptions.json')
storage = JSONStorage(SUBSCRIPTIONS_FILE, default_data={})

# File lưu trữ nhóm chứng khoán
GROUPS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'stock_groups.json')
groups_storage = JSONStorage(GROUPS_FILE, default_data={})

# Cấu hình quyền sửa/xóa nhóm
# True: Chỉ người tạo mới được sửa/xóa nhóm của mình
# False: Ai cũng có thể sửa/xóa nhóm của nhau
isOwner = False

def load_subscriptions():
    """Đọc danh sách subscriptions từ file JSON"""
    return storage.load()

def save_subscriptions(subscriptions):
    """Lưu subscriptions vào file JSON"""
    return storage.save(subscriptions)

def load_groups():
    """Đọc danh sách nhóm chứng khoán từ file JSON"""
    return groups_storage.load()

def save_groups(groups):
    """Lưu nhóm chứng khoán vào file JSON"""
    return groups_storage.save(groups)

# Sử dụng formatter từ utils
def get_color_indicator(color):
    """Wrapper cho backward compatibility"""
    return get_stock_color_indicator(color)

def sort_stocks_by_change_desc(symbols, stocks_info):
    """Sắp xếp mã theo % biến đổi giảm dần, giữ các mã không có dữ liệu ở cuối"""
    valid_symbols = [symbol for symbol in symbols if symbol in stocks_info and stocks_info[symbol] is not None]
    missing_symbols = [symbol for symbol in symbols if symbol not in stocks_info or stocks_info[symbol] is None]

    valid_symbols.sort(key=lambda symbol: stocks_info[symbol].get('change_percent', float('-inf')), reverse=True)
    return valid_symbols + missing_symbols

def send_stock_notification(bot):
    """Gửi thông báo giá chứng khoán cho các user đã đăng ký"""
    try:
        now = datetime.now()
        
        # Kiểm tra thứ (0=Monday, 6=Sunday)
        if now.weekday() > 4:  # Saturday or Sunday
            return
        
        # Kiểm tra giờ giao dịch (9h-11h45 sáng, 13h15-15h chiều)
        hour = now.hour
        minute = now.minute
        
        # Sáng: 9:00 - 11:45
        morning_session = (hour == 9 or hour == 10 or (hour == 11 and minute <= 45))
        
        # Chiều: 13:15 - 15:00
        afternoon_session = ((hour == 13 and minute >= 15) or hour == 14)
        
        if not (morning_session or afternoon_session):
            return
        
        subscriptions = load_subscriptions()
        
        for chat_id, symbols in subscriptions.items():
            if not symbols:
                continue
                
            message_parts = ["📊 **CẬP NHẬT GIÁ CHỨNG KHOÁN** 📊\n"]
            
            # Lấy thông tin tất cả mã cùng lúc - tự động fallback v2->v1
            stocks_info = get_stock_info_list_smart(symbols)
            if stocks_info:
                for symbol in sort_stocks_by_change_desc(symbols, stocks_info):
                    info = stocks_info.get(symbol)
                    if info:
                        current_price = format_price(info['current_price'])
                        change_sign = "+" if info['change_percent'] >= 0 else ""
                        message_parts.append(
                            f"{get_color_indicator(info['color'])} **{info['symbol']}**: {current_price} VNĐ "
                            f"({change_sign}{info['change_percent']:.2f}%)"
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
    
    except Exception as e:
        stock_log.error(f"Critical error in send_stock_notification: {e}")
        print(f"Critical error in send_stock_notification: {e}")
        # Không raise exception để tránh crash thread scheduler

def register_handlers(bot):
    """Đăng ký các handlers cho chức năng stock"""
    
    # Handler 1: Quản lý nhóm chứng khoán
    @bot.message_handler(commands=['cknhom', 'stockgroup', 'nhomck', 'ckn'])
    def stock_group_handler(message):
        """Quản lý nhóm chứng khoán: /cknhom hoặc /cknhom <tên nhóm>"""
        try:
            parts = message.text.strip().split()
            
            # Nếu có tên nhóm -> hiển thị thông tin các mã trong nhóm
            if len(parts) >= 2:
                group_name = parts[1].lower()
                groups = load_groups()
                
                if group_name not in groups:
                    log_user_action(message, "/cknhom", f"Group not found: {group_name}")
                    bot.send_message(
                        message.chat.id,
                        f"❌ Không tìm thấy nhóm **{group_name}**\n\n"
                        f"💡 Dùng `/cknhom` để xem danh sách nhóm",
                        parse_mode="Markdown"
                    )
                    return
                
                group_data = groups[group_name]
                symbols = group_data['symbols']
                
                log_user_action(message, "/cknhom", f"View group: {group_name} ({len(symbols)} stocks)")
                
                if not symbols:
                    bot.send_message(
                        message.chat.id,
                        f"📂 **Nhóm: {group_name.upper()}**\n\n"
                        f"❌ Nhóm này chưa có mã nào!",
                        parse_mode="Markdown"
                    )
                    return
                
                # Lấy thông tin tất cả mã trong nhóm
                stocks_info = get_stock_info_list_smart(symbols)
                
                message_parts = [f"📂 **NHÓM: {group_name.upper()}** 📂\n"]
                
                if stocks_info:
                    for symbol in sort_stocks_by_change_desc(symbols, stocks_info):
                        info = stocks_info.get(symbol)
                        if info:
                            change_sign = "+" if info['change_percent'] >= 0 else ""
                            message_parts.append(
                                f"{get_color_indicator(info['color'])} **{info['symbol']}**: "
                                f"{format_price(info['current_price'])} VNĐ "
                                f"({change_sign}{info['change_percent']:.2f}%)"
                            )
                else:
                    message_parts.append("⚠️ Không thể tải dữ liệu. Vui lòng thử lại sau.")
                
                stock_log.info(f"Group view: {group_name} | Stocks: {', '.join(symbols)} | User: {message.from_user.username} (ID: {message.from_user.id})")
                
                bot.send_message(
                    message.chat.id,
                    "\n".join(message_parts),
                    parse_mode="Markdown"
                )
            
            # Nếu không có tên nhóm -> hiển thị menu quản lý
            else:
                log_user_action(message, "/cknhom", "User opened stock group menu")
                stock_log.info(f"Stock group menu opened | User: {message.from_user.username} (ID: {message.from_user.id})")
                
                groups = load_groups()
                user_groups_count = sum(1 for g in groups.values() if g['created_by'] == message.from_user.id)
                
                markup = InlineKeyboardMarkup(row_width=1)
                buttons = [
                    InlineKeyboardButton(
                        text="➕ Thêm nhóm mới",
                        callback_data="stock_group_add"
                    ),
                    InlineKeyboardButton(
                        text="✏️ Sửa nhóm",
                        callback_data="stock_group_edit"
                    ),
                    InlineKeyboardButton(
                        text="➖ Xóa nhóm",
                        callback_data="stock_group_delete"
                    ),
                    InlineKeyboardButton(
                        text="👁️ Xem tất cả nhóm",
                        callback_data="stock_group_view_all"
                    )
                ]
                markup.add(*buttons)
                
                bot.send_message(
                    message.chat.id,
                    f"📂 **QUẢN LÝ NHÓM CHỨNG KHOÁN** 📂\n\n"
                    f"📊 Tổng số nhóm: **{len(groups)}**\n"
                    f"👤 Nhóm của bạn: **{user_groups_count}**\n\n"
                    f"💡 Sử dụng: `/cknhom <tên nhóm>` để xem nhanh",
                    parse_mode="Markdown",
                    reply_markup=markup
                )
        
        except Exception as e:
            stock_log.error(f"Error in stock_group_handler: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra, vui lòng thử lại!"
            )
    
    # Handler 2: Xem giá chứng khoán
    @bot.message_handler(commands=['stock', 'chungkhoan', 'chung', 'ck'])
    def stock_handler(message):
        """Xem giá chứng khoán: /stock VCB hoặc /stock VCB MSN HPG"""
        try:
            parts = message.text.strip().split()

            if len(parts) < 2:
                log_user_action(message, "/stock", "No symbol provided")
                bot.send_message(
                    message.chat.id,
                    "❌ Vui lòng nhập mã chứng khoán!\n\n"
                    "📝 Cách dùng:\n"
                    "• Một mã: `/ck VCB`\n"
                    "• Nhiều mã: `/ck VCB MSN HPG`",
                    parse_mode="Markdown"
                )
                return

            symbols = [s.upper() for s in parts[1:]]
            log_user_action(message, "/stock", f"Symbols: {', '.join(symbols)}")

            # Trường hợp 1 mã: hiển thị chi tiết
            if len(symbols) == 1:
                symbol = symbols[0]
                info = get_stock_info_list_smart([symbol]).get(symbol)

                if not info:
                    stock_log.warning(f"Stock not found: {symbol} | User: {message.from_user.username} (ID: {message.from_user.id})")
                    bot.send_message(
                        message.chat.id,
                        f"❌ Không tìm thấy thông tin cho mã **{symbol}**",
                        parse_mode="Markdown"
                    )
                    return

                stock_log.info(f"Stock query: {symbol} | Price: {info['current_price']} | Change: {info['change_percent']:.2f}% | User: {message.from_user.username} (ID: {message.from_user.id})")

                color_indicator = get_color_indicator(info['color'])
                change_sign = "+" if info['change_percent'] >= 0 else ""

                response = (
                    f"📈 **THÔNG TIN CHỨNG KHOÁN** 📈\n\n"
                    f"🏢 Mã: **{info['symbol']}**\n"
                    f"🏢 Tên công ty: **{info['name_company']}**\n\n"
                    f"{color_indicator} Giá hiện tại: **{format_price(info['current_price'])}** VNĐ\n"
                    f"📊 Thay đổi: **{change_sign}{info['change_percent']:.2f}%**\n\n"
                    f"🔺 Giá trần: {format_price(info['ceiling_price'])} VNĐ\n"
                    f"🔻 Giá sàn: {format_price(info['floor_price'])} VNĐ\n"
                    f"📌 Giá tham chiếu: {format_price(info['reference_price'])} VNĐ"
                )

                bot.send_message(message.chat.id, response, parse_mode="Markdown")

            # Trường hợp nhiều mã: hiển thị danh sách tóm tắt
            else:
                stocks_info = get_stock_info_list_smart(symbols)

                message_parts = ["📊 **THÔNG TIN CHỨNG KHOÁN** 📊\n"]
                not_found = []

                for symbol in sort_stocks_by_change_desc(symbols, stocks_info or {}):
                    info = stocks_info.get(symbol) if stocks_info else None
                    if info:
                        change_sign = "+" if info['change_percent'] >= 0 else ""
                        message_parts.append(
                            f"{get_color_indicator(info['color'])} **{info['symbol']}**: "
                            f"{format_price(info['current_price'])} VNĐ "
                            f"({change_sign}{info['change_percent']:.2f}%)"
                        )
                    else:
                        not_found.append(symbol)

                if not_found:
                    message_parts.append(f"\n❌ Không tìm thấy: `{', '.join(not_found)}`")

                stock_log.info(f"Multi-stock query: {', '.join(symbols)} | User: {message.from_user.username} (ID: {message.from_user.id})")

                bot.send_message(message.chat.id, "\n".join(message_parts), parse_mode="Markdown")

        except Exception as e:
            stock_log.error(f"Error in stock_handler: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra, vui lòng thử lại!"
            )
    
    # Handler callback cho quản lý nhóm CK
    @bot.callback_query_handler(func=lambda call: call.data == "stock_group_add")
    def stock_group_add_callback(call):
        """Yêu cầu người dùng nhập tên nhóm"""
        msg = bot.send_message(
            call.message.chat.id,
            "📝 **THÊM NHÓM MỚI**\n\n"
            "Bước 1/2: Nhập tên nhóm (viết không dấu)\n\n"
            "💡 VD: `bank`, `tech`, `bluechip`",
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, process_add_group_name, call.from_user.id)
        bot.answer_callback_query(call.id)
    
    def process_add_group_name(message, user_id):
        """Xử lý tên nhóm và yêu cầu nhập danh sách mã"""
        try:
            # Kiểm tra xem người gửi có phải là người đã kích hoạt lệnh không
            if message.from_user.id != user_id:
                return  # Bỏ qua nếu không phải người đã kích hoạt
            
            # Kiểm tra xem message có phải là reply không (cho group chat)
            # Nếu không phải reply và đang trong group, bỏ qua
            if message.chat.type in ['group', 'supergroup']:
                if not message.reply_to_message:
                    return  # Bỏ qua nếu không phải reply trong group
            
            group_name = message.text.strip().lower().replace(' ', '_')
            
            if not group_name or len(group_name) < 2:
                bot.send_message(
                    message.chat.id,
                    "❌ Tên nhóm quá ngắn! Vui lòng thử lại.",
                    parse_mode="Markdown"
                )
                return
            
            groups = load_groups()
            
            if group_name in groups:
                bot.send_message(
                    message.chat.id,
                    f"❌ Nhóm **{group_name}** đã tồn tại!\n\n"
                    f"💡 Vui lòng chọn tên khác hoặc sửa nhóm hiện có.",
                    parse_mode="Markdown"
                )
                return
            
            msg = bot.send_message(
                message.chat.id,
                f"📝 **THÊM NHÓM: {group_name.upper()}**\n\n"
                f"Bước 2/2: Nhập danh sách mã chứng khoán\n\n"
                f"💡 Cách nhập: `VCB BID TCB` hoặc `VCB, BID, TCB`",
                parse_mode="Markdown",
                reply_markup=ForceReply(selective=True)
            )
            bot.register_next_step_handler(msg, process_add_group_symbols, group_name, user_id)
        
        except Exception as e:
            stock_log.error(f"Error in process_add_group_name: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra, vui lòng thử lại!"
            )
    
    def process_add_group_symbols(message, group_name, user_id):
        """Xử lý danh sách mã và tạo nhóm"""
        try:
            # Kiểm tra xem người gửi có phải là người đã kích hoạt lệnh không
            if message.from_user.id != user_id:
                return  # Bỏ qua nếu không phải người đã kích hoạt
            
            # Kiểm tra xem message có phải là reply không (cho group chat)
            if message.chat.type in ['group', 'supergroup']:
                if not message.reply_to_message:
                    return  # Bỏ qua nếu không phải reply trong group
            
            input_text = message.text.strip().replace(',', ' ')
            symbols = [s.strip().upper() for s in input_text.split() if s.strip()]
            
            if not symbols:
                bot.send_message(
                    message.chat.id,
                    "❌ Vui lòng nhập ít nhất một mã chứng khoán!",
                    parse_mode="Markdown"
                )
                return
            
            # Kiểm tra tính hợp lệ của các mã
            valid_symbols = []
            invalid_symbols = []
            
            for symbol in symbols:
                info = get_stock_info(symbol)
                if info:
                    valid_symbols.append(symbol)
                else:
                    invalid_symbols.append(symbol)
            
            if not valid_symbols:
                bot.send_message(
                    message.chat.id,
                    f"❌ Không có mã hợp lệ nào!\n\n"
                    f"Các mã không tìm thấy: `{', '.join(invalid_symbols)}`",
                    parse_mode="Markdown"
                )
                return
            
            # Lưu nhóm
            groups = load_groups()
            groups[group_name] = {
                'name': group_name,
                'symbols': valid_symbols,
                'created_by': message.from_user.id
            }
            save_groups(groups)
            
            stock_log.info(f"Group created: {group_name} | Stocks: {', '.join(valid_symbols)} | User: {message.from_user.username} (ID: {message.from_user.id})")
            
            result_parts = [
                f"✅ **ĐÃ TẠO NHÓM: {group_name.upper()}**\n",
                f"📊 Số mã hợp lệ: **{len(valid_symbols)}**",
                f"Danh sách: `{', '.join(valid_symbols)}`"
            ]
            
            if invalid_symbols:
                result_parts.append(f"\n❌ Các mã không hợp lệ ({len(invalid_symbols)}): `{', '.join(invalid_symbols)}`")
            
            result_parts.append(f"\n💡 Sử dụng: `/cknhom {group_name}` để xem nhóm này")
            
            bot.send_message(
                message.chat.id,
                "\n".join(result_parts),
                parse_mode="Markdown"
            )
        
        except Exception as e:
            stock_log.error(f"Error in process_add_group_symbols: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra, vui lòng thử lại!"
            )
    
    @bot.callback_query_handler(func=lambda call: call.data == "stock_group_edit")
    def stock_group_edit_callback(call):
        """Hiển thị danh sách nhóm của user để chọn sửa"""
        groups = load_groups()
        
        # Nếu isOwner = True: chỉ hiện nhóm của user
        # Nếu isOwner = False: hiện tất cả nhóm
        if isOwner:
            user_groups = {k: v for k, v in groups.items() if v['created_by'] == call.from_user.id}
        else:
            user_groups = groups
        
        if not user_groups:
            bot.answer_callback_query(call.id, "Chưa có nhóm nào!" if not isOwner else "Bạn chưa tạo nhóm nào!")
            return
        
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton(
                text=f"✏️ {group_name.upper()} ({len(data['symbols'])} mã)",
                callback_data=f"stock_group_edit_{group_name}"
            ) for group_name, data in user_groups.items()
        ]
        markup.add(*buttons)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✏️ **CHỌN NHÓM CẦN SỬA:**",
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("stock_group_edit_"))
    def stock_group_edit_selected_callback(call):
        """Xử lý khi user chọn nhóm cần sửa"""
        group_name = call.data.replace("stock_group_edit_", "")
        groups = load_groups()
        
        if group_name not in groups:
            bot.answer_callback_query(call.id, "Nhóm không tồn tại!")
            return
        
        group_data = groups[group_name]
        current_symbols = ', '.join(group_data['symbols'])
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✏️ **SỬA NHÓM: {group_name.upper()}**\n\n"
                 f"📋 Danh sách hiện tại:\n`{current_symbols}`\n\n"
                 f"📝 Nhập danh sách mã mới:",
            parse_mode="Markdown"
        )
        
        bot.answer_callback_query(call.id)
        
        # Gửi tin nhắn mới với ForceReply thay vì dùng call.message
        msg = bot.send_message(
            call.message.chat.id,
            f"📝 Vui lòng reply tin nhắn này với danh sách mã mới cho nhóm **{group_name.upper()}**:",
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, process_edit_group_symbols, group_name, call.from_user.id)
    
    def process_edit_group_symbols(message, group_name, user_id):
        """Xử lý cập nhật danh sách mã mới cho nhóm"""
        try:
            # Kiểm tra xem người gửi có phải là người đã kích hoạt lệnh không
            if message.from_user.id != user_id:
                return  # Bỏ qua nếu không phải người đã kích hoạt
            
            # Kiểm tra xem message có phải là reply không (cho group chat)
            if message.chat.type in ['group', 'supergroup']:
                if not message.reply_to_message:
                    return  # Bỏ qua nếu không phải reply trong group
            
            input_text = message.text.strip().replace(',', ' ')
            symbols = [s.strip().upper() for s in input_text.split() if s.strip()]
            
            if not symbols:
                bot.send_message(
                    message.chat.id,
                    "❌ Vui lòng nhập ít nhất một mã chứng khoán!",
                    parse_mode="Markdown"
                )
                return
            
            # Kiểm tra tính hợp lệ
            valid_symbols = []
            invalid_symbols = []
            
            for symbol in symbols:
                info = get_stock_info(symbol)
                if info:
                    valid_symbols.append(symbol)
                else:
                    invalid_symbols.append(symbol)
            
            if not valid_symbols:
                bot.send_message(
                    message.chat.id,
                    f"❌ Không có mã hợp lệ nào!\n\n"
                    f"Các mã không tìm thấy: `{', '.join(invalid_symbols)}`",
                    parse_mode="Markdown"
                )
                return
            
            # Cập nhật nhóm
            groups = load_groups()
            groups[group_name]['symbols'] = valid_symbols
            save_groups(groups)
            
            stock_log.info(f"Group updated: {group_name} | New stocks: {', '.join(valid_symbols)} | User: {message.from_user.username} (ID: {message.from_user.id})")
            
            result_parts = [
                f"✅ **ĐÃ CẬP NHẬT NHÓM: {group_name.upper()}**\n",
                f"📊 Số mã: **{len(valid_symbols)}**",
                f"Danh sách: `{', '.join(valid_symbols)}`"
            ]
            
            if invalid_symbols:
                result_parts.append(f"\n❌ Các mã không hợp lệ: `{', '.join(invalid_symbols)}`")
            
            bot.send_message(
                message.chat.id,
                "\n".join(result_parts),
                parse_mode="Markdown"
            )
        
        except Exception as e:
            stock_log.error(f"Error in process_edit_group_symbols: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra, vui lòng thử lại!"
            )
    
    @bot.callback_query_handler(func=lambda call: call.data == "stock_group_delete")
    def stock_group_delete_callback(call):
        """Hiển thị danh sách nhóm của user để xóa"""
        groups = load_groups()
        
        # Nếu isOwner = True: chỉ hiện nhóm của user
        # Nếu isOwner = False: hiện tất cả nhóm
        if isOwner:
            user_groups = {k: v for k, v in groups.items() if v['created_by'] == call.from_user.id}
        else:
            user_groups = groups
        
        if not user_groups:
            bot.answer_callback_query(call.id, "Chưa có nhóm nào!" if not isOwner else "Bạn chưa tạo nhóm nào!")
            return
        
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton(
                text=f"🗑️ {group_name.upper()} ({len(data['symbols'])} mã)",
                callback_data=f"stock_group_del_{group_name}"
            ) for group_name, data in user_groups.items()
        ]
        markup.add(*buttons)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🗑️ **CHỌN NHÓM CẦN XÓA:**",
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("stock_group_del_"))
    def stock_group_delete_confirm_callback(call):
        """Xử lý xóa nhóm"""
        group_name = call.data.replace("stock_group_del_", "")
        groups = load_groups()
        
        # Kiểm tra quyền xóa
        can_delete = False
        if group_name in groups:
            if isOwner:
                # Chỉ người tạo mới được xóa
                can_delete = groups[group_name]['created_by'] == call.from_user.id
            else:
                # Ai cũng có thể xóa
                can_delete = True
        
        if can_delete:
            del groups[group_name]
            save_groups(groups)
            
            stock_log.info(f"Group deleted: {group_name} | User: {call.from_user.username} (ID: {call.from_user.id})")
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Đã xóa nhóm **{group_name.upper()}**!",
                parse_mode="Markdown"
            )
        else:
            bot.answer_callback_query(call.id, "Không thể xóa nhóm này!")
    
    @bot.callback_query_handler(func=lambda call: call.data == "stock_group_view_all")
    def stock_group_view_all_callback(call):
        """Hiển thị tất cả nhóm"""
        try:
            bot.answer_callback_query(call.id, "Đang tải...")
        except:
            pass
        
        groups = load_groups()
        
        if not groups:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="❌ Chưa có nhóm nào!\n\n"
                     "💡 Dùng `/cknhom` để tạo nhóm mới",
                parse_mode="Markdown"
            )
            return
        
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton(
                text=f"📂 {group_name.upper()} ({len(data['symbols'])} mã)",
                callback_data=f"stock_group_show_{group_name}"
            ) for group_name, data in groups.items()
        ]
        markup.add(*buttons)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"👁️ **TẤT CẢ NHÓM CHỨNG KHOÁN**\n\n"
                 f"📊 Tổng số: **{len(groups)}** nhóm\n\n"
                 f"Chọn nhóm để xem chi tiết:",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("stock_group_show_"))
    def stock_group_show_callback(call):
        """Hiển thị chi tiết một nhóm"""
        try:
            bot.answer_callback_query(call.id, "Đang tải...")
        except:
            pass
        
        group_name = call.data.replace("stock_group_show_", "")
        groups = load_groups()
        
        if group_name not in groups:
            bot.answer_callback_query(call.id, "Nhóm không tồn tại!")
            return
        
        group_data = groups[group_name]
        symbols = group_data['symbols']
        
        if not symbols:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"📂 **Nhóm: {group_name.upper()}**\n\n"
                     f"❌ Nhóm này chưa có mã nào!",
                parse_mode="Markdown"
            )
            return
        
        # Lấy thông tin tất cả mã trong nhóm
        stocks_info = get_stock_info_list_smart(symbols)
        
        message_parts = [f"📂 **NHÓM: {group_name.upper()}** 📂\n"]
        
        if stocks_info:
            for symbol in sort_stocks_by_change_desc(symbols, stocks_info):
                info = stocks_info.get(symbol)
                if info:
                    change_sign = "+" if info['change_percent'] >= 0 else ""
                    message_parts.append(
                        f"{get_color_indicator(info['color'])} **{info['symbol']}**: "
                        f"{format_price(info['current_price'])} VNĐ "
                        f"({change_sign}{info['change_percent']:.2f}%)"
                    )
        else:
            message_parts.append("⚠️ Không thể tải dữ liệu. Vui lòng thử lại sau.")
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="\n".join(message_parts),
                parse_mode="Markdown"
            )
        except Exception as e:
            stock_log.error(f"Error editing message in stock_group_show_callback: {e}")
    
    # Handler 3: Quản lý subscriptions
    @bot.message_handler(commands=['stockwatch', 'theodoick', 'ckwatch'])
    def stock_watch_handler(message):
        """Menu quản lý theo dõi chứng khoán"""
        log_user_action(message, "/stockwatch", "User opened stock watch menu")
        stock_log.info(f"Stock watch menu opened | User: {message.from_user.username} (ID: {message.from_user.id})")
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
            f"🔔 Nhận thông báo giá mỗi 2 phút\n"
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
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, process_add_stock, call.from_user.id)
        bot.answer_callback_query(call.id)
    
    def process_add_stock(message, user_id):
        """Xử lý thêm mã chứng khoán (hỗ trợ nhiều mã cùng lúc)"""
        try:
            # Kiểm tra xem người gửi có phải là người đã kích hoạt lệnh không
            if message.from_user.id != user_id:
                return  # Bỏ qua nếu không phải người đã kích hoạt
            
            # Kiểm tra xem message có phải là reply không (cho group chat)
            if message.chat.type in ['group', 'supergroup']:
                if not message.reply_to_message:
                    return  # Bỏ qua nếu không phải reply trong group
            
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
                stock_log.info(f"Added stocks: {', '.join(valid_symbols)} | Total: {len(subscriptions[chat_id])} | User: {message.from_user.username} (ID: {message.from_user.id})")
            
            if invalid_symbols:
                stock_log.warning(f"Invalid stocks attempted: {', '.join(invalid_symbols)} | User: {message.from_user.username}")
            
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
            
            stock_log.info(f"Stock removed: {symbol} | Remaining: {len(subscriptions[chat_id])} | User: {call.from_user.username} (ID: {call.from_user.id})")
            
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
        # Answer callback query NGAY LẬP TỨC để tránh timeout
        try:
            bot.answer_callback_query(call.id, "Đang tải dữ liệu...")
        except:
            pass  # Bỏ qua nếu callback đã hết hạn
        
        chat_id = str(call.message.chat.id)
        subscriptions = load_subscriptions()
        current_symbols = subscriptions.get(chat_id, [])
        
        if not current_symbols:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="❌ Chưa có mã nào!",
                parse_mode="Markdown"
            )
            return
        
        message_parts = ["📋 **DANH SÁCH ĐANG THEO DÕI** 📋\n"]
        
        # Sử dụng smart API với fallback v2->v1
        stocks_info = get_stock_info_list_smart(current_symbols)
        
        if stocks_info:
            for symbol in sort_stocks_by_change_desc(current_symbols, stocks_info):
                info = stocks_info.get(symbol)
                if info:
                    current_price = format_price(info['current_price'])
                    change_sign = "+" if info['change_percent'] >= 0 else ""
                    message_parts.append(
                        f"{get_color_indicator(info['color'])} **{symbol}**: "
                        f"{current_price} VNĐ ({change_sign}{info['change_percent']:.2f}%)"
                    )
        else:
            message_parts.append("\n⚠️ Không thể tải dữ liệu. Vui lòng thử lại sau.")
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="\n".join(message_parts),
                parse_mode="Markdown"
            )
        except Exception as e:
            stock_log.error(f"Error editing message: {e}")
    
    # Đăng ký scheduler để gửi thông báo mỗi 5 phút
    schedule.every(2).minutes.do(send_stock_notification, bot=bot)
    
    # Khởi động scheduler
    start_scheduler()
    
    stock_log.info("Stock handlers registered successfully")
