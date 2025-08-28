import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logs.logs import setup_logger 
from get_api.lunar_calendar import solar_to_lunar, lunar_to_solar, get_weekday_vietnamese, get_weekday_emoji
from datetime import datetime
import re

lunar_log = setup_logger('lunar.log')

def register_handlers(bot):
    @bot.message_handler(commands=['lunar', 'lichconvert', 'amlich'])
    def lunar_handler(message):
        """Handler chính cho chức năng chuyển đổi lịch"""
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton(text="🌞 Dương → Âm", callback_data="convert_solar_to_lunar"),
            InlineKeyboardButton(text="🌙 Âm → Dương", callback_data="convert_lunar_to_solar"),
            InlineKeyboardButton(text="📅 Hôm nay", callback_data="convert_today")
        ]
        markup.add(*buttons)
        
        bot.send_message(
            message.chat.id,
            "🗓️ **CHUYỂN ĐỔI LỊCH** 🗓️\n\n"
            "Chọn loại chuyển đổi bạn muốn thực hiện:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("convert_"))
    def handle_convert_choice(call):
        """Xử lý lựa chọn loại chuyển đổi"""
        try:
            choice = call.data.split("_", 1)[1]
            
            if choice == "today":
                # Chuyển đổi ngày hôm nay
                today = datetime.now()
                result = solar_to_lunar(today.day, today.month, today.year)
                
                if result:
                    # Tính thứ (chỉ cần tính 1 lần vì cùng ngày)
                    weekday = get_weekday_vietnamese(today.day, today.month, today.year)
                    emoji = get_weekday_emoji(today.day, today.month, today.year)
                    
                    message = format_conversion_result(
                        f"{today.day:02d}/{today.month:02d}/{today.year}",
                        f"{result['day']:02d}/{result['month']:02d}/{result['year']}",
                        result,
                        "dương sang âm lịch",
                        weekday,
                        emoji
                    )
                    bot.edit_message_text(
                        message,
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="Markdown"
                    )
                else:
                    bot.answer_callback_query(call.id, "❌ Có lỗi khi chuyển đổi!")
                return
            
            # Yêu cầu nhập ngày
            instruction = ""
            if choice == "solar_to_lunar":
                instruction = (
                    "🌞 **CHUYỂN ĐỔI DƯƠNG LỊCH SANG ÂM LỊCH**\n\n"
                    "📝 Nhập ngày dương lịch theo định dạng:\n"
                    "• `dd/mm/yyyy` (VD: 29/01/2025)\n"
                    "• `dd-mm-yyyy` (VD: 29-01-2025)\n"
                    "• `dd.mm.yyyy` (VD: 29.01.2025)\n\n"
                    "💡 Ví dụ: 29/01/2025"
                )
            else:  # lunar_to_solar
                instruction = (
                    "🌙 **CHUYỂN ĐỔI ÂM LỊCH SANG DƯƠNG LỊCH**\n\n"
                    "📝 Nhập ngày âm lịch theo định dạng:\n"
                    "• `dd/mm/yyyy` (VD: 01/01/2025)\n"
                    "• `dd-mm-yyyy` (VD: 01-01-2025)\n"
                    "• `dd.mm.yyyy` (VD: 01.01.2025)\n\n"
                    "💡 Ví dụ: 01/01/2025"
                )
            
            bot.edit_message_text(
                instruction,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
            
            # Đăng ký handler để nhận input ngày
            bot.register_next_step_handler(call.message, process_date_input, choice)
            
        except Exception as e:
            lunar_log.error(f"Error in handle_convert_choice: {e}")
            bot.answer_callback_query(call.id, "❌ Có lỗi xảy ra!")

    def process_date_input(message, conversion_type):
        """Xử lý input ngày từ người dùng"""
        try:
            date_text = message.text.strip()
            
            # Parse ngày từ text
            day, month, year = parse_date(date_text)
            
            if not day or not month or not year:
                bot.send_message(
                    message.chat.id,
                    "❌ **Định dạng ngày không hợp lệ!**\n\n"
                    "📝 Vui lòng nhập theo định dạng: dd/mm/yyyy\n"
                    "💡 Ví dụ: 29/01/2025",
                    parse_mode="Markdown"
                )
                return
            
            # Validate ngày
            if not validate_date(day, month, year):
                bot.send_message(
                    message.chat.id,
                    "❌ **Ngày không hợp lệ!**\n\n"
                    "📅 Vui lòng kiểm tra lại ngày/tháng/năm",
                    parse_mode="Markdown"
                )
                return
            
            # Thực hiện chuyển đổi
            if conversion_type == "solar_to_lunar":
                result = solar_to_lunar(day, month, year)
                conversion_text = "dương lịch sang âm lịch"
                input_date = f"{day:02d}/{month:02d}/{year}"
                
                if result:
                    output_date = f"{result['day']:02d}/{result['month']:02d}/{result['year']}"
                    # Tính thứ (chỉ cần tính 1 lần)
                    weekday = get_weekday_vietnamese(day, month, year)
                    emoji = get_weekday_emoji(day, month, year)
                else:
                    output_date = None
                    weekday = emoji = None
                    
            else:  # lunar_to_solar
                result = lunar_to_solar(day, month, year)
                conversion_text = "âm lịch sang dương lịch"
                input_date = f"{day:02d}/{month:02d}/{year}"
                
                if result:
                    output_date = f"{result['day']:02d}/{result['month']:02d}/{result['year']}"
                    # Tính thứ (chỉ cần tính 1 lần)
                    weekday = get_weekday_vietnamese(result['day'], result['month'], result['year'])
                    emoji = get_weekday_emoji(result['day'], result['month'], result['year'])
                else:
                    output_date = None
                    weekday = emoji = None
            
            if result:
                response_message = format_conversion_result(
                    input_date, output_date, result, conversion_text,
                    weekday, emoji
                )
                
                # Thêm nút chuyển đổi lại
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton(
                        text="🔄 Chuyển đổi khác", 
                        callback_data="convert_menu"
                    )
                )
                
                bot.send_message(
                    message.chat.id,
                    response_message,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "❌ **Không thể chuyển đổi!**\n\n"
                    "🔍 Vui lòng kiểm tra lại ngày hoặc thử lại sau",
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            lunar_log.error(f"Error in process_date_input: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Có lỗi xảy ra khi xử lý. Vui lòng thử lại!"
            )

    @bot.callback_query_handler(func=lambda call: call.data == "convert_menu")
    def back_to_menu(call):
        """Quay lại menu chuyển đổi"""
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton(text="🌞 Dương → Âm", callback_data="convert_solar_to_lunar"),
            InlineKeyboardButton(text="🌙 Âm → Dương", callback_data="convert_lunar_to_solar"),
            InlineKeyboardButton(text="📅 Hôm nay", callback_data="convert_today")
        ]
        markup.add(*buttons)
        
        bot.edit_message_text(
            "🗓️ **CHUYỂN ĐỔI LỊCH** 🗓️\n\n"
            "Chọn loại chuyển đổi bạn muốn thực hiện:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

def parse_date(date_text):
    """Parse ngày từ text input"""
    try:
        # Thử các định dạng khác nhau
        patterns = [
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})',  # dd/mm/yyyy, dd-mm-yyyy, dd.mm.yyyy
            r'(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})',  # yyyy/mm/dd, yyyy-mm-dd, yyyy.mm.dd
        ]
        
        for pattern in patterns:
            match = re.match(pattern, date_text)
            if match:
                if len(match.group(3)) == 4:  # dd/mm/yyyy format
                    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                else:  # yyyy/mm/dd format
                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                return day, month, year
        
        return None, None, None
    except:
        return None, None, None

def validate_date(day, month, year):
    """Validate ngày tháng năm"""
    try:
        if year < 1900 or year > 2100:
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        
        # Kiểm tra ngày hợp lệ trong tháng
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Năm nhuận
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            days_in_month[1] = 29
        
        return day <= days_in_month[month - 1]
    except:
        return False

def format_conversion_result(input_date, output_date, result, conversion_type, 
                           weekday=None, emoji=None):
    """Format kết quả chuyển đổi thành message đẹp"""
    message = "✅ **KẾT QUẢ CHUYỂN ĐỔI** ✅\n\n"
    
    # Thêm thông tin thứ (chung cho cả hai ngày)
    weekday_info = ""
    if weekday and emoji:
        weekday_info = f" ({emoji} {weekday})"
    
    if "dương lịch sang âm lịch" in conversion_type:
        # Dương → Âm
        message += f"📅 **Dương lịch:** {input_date}{weekday_info}\n"
        message += f"🌙 **Âm lịch:** {output_date}\n\n"
    else:
        # Âm → Dương  
        message += f"🌙 **Âm lịch:** {input_date}{weekday_info}\n"
        message += f"📅 **Dương lịch:** {output_date}\n\n"
    
    # Thêm thông tin can chi nếu có
    if result.get('heavenlyStem') and result.get('earthlyBranch'):
        message += f"🎋 **Can Chi:** {result['heavenlyStem']} {result['earthlyBranch']}\n"
    
    if result.get('sexagenaryCycle'):
        message += f"🗓️ **Năm:** {result['sexagenaryCycle']}\n"
    
    message += f"\n📊 **Loại chuyển đổi:** {conversion_type}"
    
    return message
