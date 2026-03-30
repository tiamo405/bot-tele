import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schedule
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

import config
from get_api.phatnguoi import search_phat_nguoi, normalize_plate
from logs.logs import setup_logger
from utils.json_storage import JSONStorage
from utils.log_helper import log_user_action
from utils.scheduler import start_scheduler


phatnguoi_log = setup_logger('phatnguoi.log')

VEHICLE_FILE = os.path.join(config.DATA_DIR, 'phatnguoi_vehicles.json')
vehicle_storage = JSONStorage(VEHICLE_FILE, default_data={})


def load_vehicle_data():
    data = vehicle_storage.load()
    return data if isinstance(data, dict) else {}


def save_vehicle_data(data):
    return vehicle_storage.save(data)


def normalize_vehicle_type(vehicle_type):
    vt = (vehicle_type or 'auto').strip().lower()

    if vt in ('car', 'oto', 'o-to', 'xeoto', 'xe-oto'):
        return 'car'
    if vt in ('moto', 'xemay', 'xe-may'):
        return 'moto'
    return 'auto'


def vehicle_type_label(vehicle_type):
    vt = normalize_vehicle_type(vehicle_type)
    if vt == 'car':
        return 'Ô tô'
    if vt == 'moto':
        return 'Xe máy'
    return 'Tự động'


def vehicle_key(plate):
    return ''.join(ch for ch in normalize_plate(plate) if ch.isalnum())


def parse_plate_and_type(input_text):
    text = (input_text or '').strip()
    if not text:
        return '', 'auto'

    parts = text.split()
    maybe_type = parts[-1].lower()

    if maybe_type in ('car', 'moto', 'oto', 'o-to', 'xeoto', 'xe-oto', 'xemay', 'xe-may'):
        vehicle_type = normalize_vehicle_type(maybe_type)
        plate = normalize_plate(' '.join(parts[:-1]))
    else:
        vehicle_type = 'auto'
        plate = normalize_plate(text)

    return plate, vehicle_type


def get_user_record(all_data, user_id):
    user_key = str(user_id)
    record = all_data.get(user_key, {})

    if not isinstance(record, dict):
        record = {}

    vehicles = record.get('vehicles')
    if not isinstance(vehicles, list):
        vehicles = []

    record['vehicles'] = vehicles
    return record


def get_user_vehicles(user_id):
    all_data = load_vehicle_data()
    return get_user_record(all_data, user_id).get('vehicles', [])


def save_user_chat_id(user_id, chat_id):
    all_data = load_vehicle_data()
    record = get_user_record(all_data, user_id)
    record['chat_id'] = chat_id
    all_data[str(user_id)] = record
    save_vehicle_data(all_data)


def add_vehicle_for_user(user_id, chat_id, plate, vehicle_type='auto'):
    all_data = load_vehicle_data()
    user_key = str(user_id)
    record = get_user_record(all_data, user_id)
    vehicles = record.get('vehicles', [])

    plate_norm = normalize_plate(plate)
    plate_norm_key = vehicle_key(plate_norm)
    vt_norm = normalize_vehicle_type(vehicle_type)

    for vehicle in vehicles:
        if vehicle_key(vehicle.get('plate', '')) == plate_norm_key:
            old_type = normalize_vehicle_type(vehicle.get('vehicle_type', 'auto'))
            if old_type != vt_norm and vt_norm != 'auto':
                vehicle['vehicle_type'] = vt_norm
                record['chat_id'] = chat_id
                record['vehicles'] = vehicles
                all_data[user_key] = record
                save_vehicle_data(all_data)
                return 'updated', len(vehicles)
            return 'exists', len(vehicles)

    vehicles.append({
        'plate': plate_norm,
        'vehicle_type': vt_norm,
    })

    record['chat_id'] = chat_id
    record['vehicles'] = vehicles
    all_data[user_key] = record
    save_vehicle_data(all_data)
    return 'added', len(vehicles)


def remove_vehicle_for_user(user_id, index):
    all_data = load_vehicle_data()
    user_key = str(user_id)
    record = get_user_record(all_data, user_id)
    vehicles = record.get('vehicles', [])

    if index < 0 or index >= len(vehicles):
        return None

    removed = vehicles.pop(index)
    record['vehicles'] = vehicles
    all_data[user_key] = record
    save_vehicle_data(all_data)
    return removed


def shorten_text(value, max_len=200):
    text = str(value or '').strip()
    if not text:
        return ''
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + '...'


def format_lookup_message(lookup_result):
    if not lookup_result.get('success'):
        return f"❌ Không thể tra cứu: {lookup_result.get('message', 'Lỗi không xác định')}"

    data = lookup_result.get('data') or {}

    plate = data.get('plate_formatted') or data.get('plate') or 'N/A'
    total = int(data.get('total_violations') or 0)
    unpaid = int(data.get('unpaid_count') or 0)
    paid = int(data.get('paid_count') or 0)
    last_updated = data.get('last_updated') or 'N/A'
    used_type = lookup_result.get('vehicle_type', 'auto')

    lines = [
        '🚔 KẾT QUẢ TRA CỨU PHẠT NGUỘI',
        f'Biển số: {plate}',
        f'Loại xe: {vehicle_type_label(used_type)}',
        f'Cập nhật: {last_updated}',
        f'Tổng vi phạm: {total} | Chưa xử phạt: {unpaid} | Đã xử phạt: {paid}',
    ]

    violations = data.get('violations') or []
    if not violations:
        lines.append('✅ Không có lỗi vi phạm.')
        return '\n'.join(lines)

    lines.append('')
    lines.append('📌 Chi tiết lỗi:')

    max_items = 3
    for idx, violation in enumerate(violations[:max_items], start=1):
        title = shorten_text(violation.get('title'), 180) or 'Không có mô tả'
        time_text = shorten_text(violation.get('time'), 80)
        location = shorten_text(violation.get('location'), 160)
        status = shorten_text(violation.get('status_text'), 80)
        unit = shorten_text(violation.get('unit'), 140)

        lines.append(f"{idx}. {title}")
        if time_text:
            lines.append(f"   • Thời gian: {time_text}")
        if location:
            lines.append(f"   • Địa điểm: {location}")
        if status:
            lines.append(f"   • Trạng thái: {status}")
        if unit:
            lines.append(f"   • Đơn vị xử lý: {unit}")

    if len(violations) > max_items:
        lines.append(f"... và {len(violations) - max_items} lỗi khác.")

    return '\n'.join(lines)


def format_vehicle_list(vehicles):
    if not vehicles:
        return 'Chưa đăng ký xe nào.'

    lines = []
    for idx, vehicle in enumerate(vehicles, start=1):
        plate = vehicle.get('plate', 'N/A')
        vt = vehicle_type_label(vehicle.get('vehicle_type', 'auto'))
        lines.append(f"{idx}. {plate} ({vt})")

    return '\n'.join(lines)


def check_saved_vehicles(user_id):
    vehicles = get_user_vehicles(user_id)
    if not vehicles:
        return "❌ Bạn chưa đăng ký xe nào.\nDùng /pn để thêm xe."

    lines = ['🚔 KẾT QUẢ TRA CỨU XE ĐÃ ĐĂNG KÝ']
    has_violation = False

    for vehicle in vehicles:
        plate = normalize_plate(vehicle.get('plate', ''))
        vt = normalize_vehicle_type(vehicle.get('vehicle_type', 'auto'))
        result = search_phat_nguoi(plate, vt)

        if not result.get('success'):
            lines.append(f"⚠️ {plate}: Không tra cứu được")
            continue

        data = result.get('data') or {}
        total = int(data.get('total_violations') or 0)
        unpaid = int(data.get('unpaid_count') or 0)

        if total > 0:
            has_violation = True
            lines.append(f"❌ {plate}: {total} lỗi ({unpaid} chưa xử phạt)")
        else:
            lines.append(f"✅ {plate}: Không có lỗi")

    lines.append('')
    if has_violation:
        lines.append('⚠️ Có xe đang có vi phạm, dùng `/pn biển-số` để xem chi tiết.')
    else:
        lines.append('✅ Tất cả xe đang không có vi phạm.')

    return '\n'.join(lines)


def send_daily_phatnguoi_check(bot):
    """Tự động kiểm tra mỗi ngày lúc 09:00 và gửi kết quả cho user đã đăng ký."""
    try:
        all_data = load_vehicle_data()
        if not all_data:
            return

        date_text = datetime.now().strftime('%d/%m/%Y')

        for user_key, record in all_data.items():
            if not isinstance(record, dict):
                continue

            chat_id = record.get('chat_id')
            vehicles = record.get('vehicles', [])

            if not chat_id or not vehicles:
                continue

            lines = [f"⏰ KIỂM TRA PHẠT NGUỘI 09:00 ({date_text})"]
            has_violation = False
            has_error = False

            for vehicle in vehicles:
                plate = normalize_plate(vehicle.get('plate', ''))
                vt = normalize_vehicle_type(vehicle.get('vehicle_type', 'auto'))

                if not plate:
                    continue

                result = search_phat_nguoi(plate, vt)

                if not result.get('success'):
                    has_error = True
                    lines.append(f"⚠️ {plate}: Không tra cứu được")
                    continue

                data = result.get('data') or {}
                total = int(data.get('total_violations') or 0)
                unpaid = int(data.get('unpaid_count') or 0)

                if total > 0:
                    has_violation = True
                    lines.append(f"❌ {plate}: {total} lỗi ({unpaid} chưa xử phạt)")
                else:
                    lines.append(f"✅ {plate}: Không có lỗi")

            if len(lines) == 1:
                continue

            if has_violation:
                lines.insert(1, '🚨 Phát hiện xe có vi phạm, bạn nên kiểm tra chi tiết bằng /pn biển-số')
            elif has_error:
                lines.insert(1, 'ℹ️ Có xe chưa tra cứu được, bạn thử kiểm tra lại thủ công bằng /pn')
            else:
                lines.insert(1, '🎉 Không phát hiện vi phạm mới.')

            try:
                bot.send_message(int(chat_id), '\n'.join(lines), parse_mode='Markdown')
                phatnguoi_log.info(f"Daily check sent to user {user_key} | chat_id={chat_id}")
            except Exception as send_exc:
                phatnguoi_log.error(f"Failed to send daily check to user {user_key}: {send_exc}")

    except Exception as exc:
        phatnguoi_log.error(f"Critical error in send_daily_phatnguoi_check: {exc}")


def register_handlers(bot):
    @bot.message_handler(commands=['phatnguoi', 'pn'])
    def handle_phatnguoi(message):
        """
        /phatnguoi hoặc /pn -> mở menu
        /phatnguoi <bien-so> [car|moto] -> tra cứu nhanh
        """
        parts = message.text.strip().split()
        save_user_chat_id(message.from_user.id, message.chat.id)

        if len(parts) >= 2:
            query_text = ' '.join(parts[1:]).strip()
            plate, vehicle_type = parse_plate_and_type(query_text)

            if not plate:
                bot.send_message(
                    message.chat.id,
                    "❌ Biển số không hợp lệ.\nVD: /pn 30A-123.45 hoặc /pn 30A-123.45 car"
                )
                return

            log_user_action(message, '/pn', f'Quick lookup: {plate} ({vehicle_type})')
            phatnguoi_log.info(f"Quick lookup | plate={plate} | type={vehicle_type} | user={message.from_user.id}")

            result = search_phat_nguoi(plate, vehicle_type)
            bot.send_message(message.chat.id, format_lookup_message(result))
            return

        log_user_action(message, '/pn', 'Open phat nguoi menu')

        vehicles = get_user_vehicles(message.from_user.id)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton('🔎 Tra cứu xe đã lưu', callback_data='pn_lookup'),
            InlineKeyboardButton('➕ Thêm xe', callback_data='pn_add'),
            InlineKeyboardButton('➖ Xóa xe', callback_data='pn_remove')
        )

        bot.send_message(
            message.chat.id,
            "🚔 QUẢN LÝ TRA CỨU PHẠT NGUỘI\n\n"
            "• /pn biển-số -> tra cứu nhanh\n"
            "• Có thể thêm loại xe: car hoặc moto\n"
            "  VD: /pn 30A-123.45 car\n\n"
            "🚗 Xe đã đăng ký:\n"
            f"{format_vehicle_list(vehicles)}",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data == 'pn_lookup')
    def pn_lookup_callback(call):
        try:
            bot.answer_callback_query(call.id, 'Đang tra cứu...')
        except Exception:
            pass

        save_user_chat_id(call.from_user.id, call.message.chat.id)
        result_text = check_saved_vehicles(call.from_user.id)
        bot.send_message(call.message.chat.id, result_text, parse_mode='Markdown')

    @bot.callback_query_handler(func=lambda call: call.data == 'pn_add')
    def pn_add_callback(call):
        msg = bot.send_message(
            call.message.chat.id,
            "📝 Nhập biển số cần thêm\n"
            "Có thể nhập kèm loại xe ở cuối: car/moto\n\n"
            "VD: 30A-123.45 car\n"
            "VD: 29B1-12345 moto\n"
            "Nếu không nhập loại, bot sẽ để chế độ tự động.",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, process_add_vehicle, call.from_user.id, call.message.chat.id)

        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass

    def process_add_vehicle(message, expected_user_id, expected_chat_id):
        try:
            if message.from_user.id != expected_user_id:
                return

            if message.chat.type in ['group', 'supergroup'] and not message.reply_to_message:
                return

            plate, vehicle_type = parse_plate_and_type(message.text or '')
            if not plate:
                bot.send_message(
                    message.chat.id,
                    "❌ Biển số không hợp lệ.\nVD: 30A-123.45 car"
                )
                return

            status, total = add_vehicle_for_user(
                user_id=expected_user_id,
                chat_id=expected_chat_id,
                plate=plate,
                vehicle_type=vehicle_type,
            )

            if status == 'added':
                text = (
                    f"✅ Đã thêm biển số: {plate} ({vehicle_type_label(vehicle_type)})\n"
                    f"📋 Tổng xe đã đăng ký: {total}"
                )
            elif status == 'updated':
                text = (
                    f"ℹ️ Biển số {plate} đã tồn tại, đã cập nhật loại xe thành {vehicle_type_label(vehicle_type)}\n"
                    f"📋 Tổng xe đã đăng ký: {total}"
                )
            else:
                text = (
                    f"ℹ️ Biển số {plate} đã tồn tại trong danh sách.\n"
                    f"📋 Tổng xe đã đăng ký: {total}"
                )

            phatnguoi_log.info(
                f"Add vehicle status={status} | user={expected_user_id} | plate={plate} | type={vehicle_type}"
            )
            bot.send_message(message.chat.id, text)

        except Exception as exc:
            phatnguoi_log.error(f"Error in process_add_vehicle: {exc}")
            bot.send_message(message.chat.id, "❌ Có lỗi xảy ra khi thêm xe, vui lòng thử lại.")

    @bot.callback_query_handler(func=lambda call: call.data == 'pn_remove')
    def pn_remove_callback(call):
        vehicles = get_user_vehicles(call.from_user.id)
        if not vehicles:
            bot.answer_callback_query(call.id, 'Bạn chưa có xe nào để xóa.')
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for idx, vehicle in enumerate(vehicles):
            plate = vehicle.get('plate', 'N/A')
            vt = vehicle_type_label(vehicle.get('vehicle_type', 'auto'))
            markup.add(InlineKeyboardButton(f"❌ {plate} ({vt})", callback_data=f"pn_del_{idx}"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='🗑️ Chọn biển số cần xóa:',
            reply_markup=markup
        )

        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass

    @bot.callback_query_handler(func=lambda call: call.data.startswith('pn_del_'))
    def pn_delete_callback(call):
        try:
            index = int(call.data.replace('pn_del_', ''))
        except ValueError:
            bot.answer_callback_query(call.id, 'Dữ liệu không hợp lệ.')
            return

        removed = remove_vehicle_for_user(call.from_user.id, index)
        if not removed:
            bot.answer_callback_query(call.id, 'Không tìm thấy xe cần xóa.')
            return

        remaining = get_user_vehicles(call.from_user.id)
        removed_plate = removed.get('plate', 'N/A')

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=(
                f"✅ Đã xóa biển số: {removed_plate}\n\n"
                f"🚗 Danh sách còn lại:\n{format_vehicle_list(remaining)}"
            )
        )

        phatnguoi_log.info(f"Vehicle removed | user={call.from_user.id} | plate={removed_plate}")

        try:
            bot.answer_callback_query(call.id, 'Đã xóa thành công')
        except Exception:
            pass

    schedule.every().sunday.at('09:00').do(send_daily_phatnguoi_check, bot=bot)
    start_scheduler()

    phatnguoi_log.info('Phat nguoi handlers registered successfully')
