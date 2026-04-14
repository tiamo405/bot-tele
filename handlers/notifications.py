from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from utils.log_helper import log_user_action
from utils.notification_registry import (
    add_chat_id,
    get_channel_info,
    get_channel_members,
    find_chat_assignments,
    list_all_channels,
    remove_chat_id,
    set_channel_enabled,
)


def _is_admin_user(message):
    return message.from_user and message.from_user.id == getattr(config, "ID_ADMIN", None)


def _deny_if_not_admin(message, bot):
    if _is_admin_user(message):
        return False
    bot.send_message(message.chat.id, "Bạn không có quyền dùng lệnh này.")
    return True


def _group_name(message):
    return getattr(message.chat, "title", None) or str(message.chat.id)


def _format_channel_line(channel_info):
    status = "BẬT" if channel_info["enabled"] else "TẮT"
    return f"• {channel_info['key']} | {channel_info['title']} | {status} | {len(channel_info['chat_ids'])} nhóm"


def _render_menu(bot, message):
    channels = list_all_channels()
    markup = InlineKeyboardMarkup(row_width=1)

    for channel in channels[:8]:
        markup.add(
            InlineKeyboardButton(
                text=f"{channel['title']} ({'Bật' if channel['enabled'] else 'Tắt'})",
                callback_data=f"notif:toggle:{channel['key']}"
            )
        )

    markup.add(
        InlineKeyboardButton(text="➕ Gắn nhóm hiện tại", callback_data="notif:join_current"),
        InlineKeyboardButton(text="➖ Bỏ nhóm hiện tại", callback_data="notif:leave_current"),
    )

    bot.send_message(
        message.chat.id,
        "📣 QUẢN LÝ THÔNG BÁO\n\n"
        "Dùng menu này để bật/tắt từng loại thông báo bằng nút bấm.\n"
        "Nếu mở từ nhóm, bạn có thể gắn/bỏ chính nhóm đó khỏi kênh đang chọn.",
        reply_markup=markup
    )


def _render_lookup_menu(bot, message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="🔎 Tra cứu chat ID", callback_data="notif:lookup"),
        InlineKeyboardButton(text="📋 Xem kênh và nhóm", callback_data="notif:listdetail"),
    )

    bot.send_message(
        message.chat.id,
        "🔍 TRA CỨU NHÓM THEO CHAT ID\n\n"
        "Bạn có thể xem một nhóm ID đang được gắn với chức năng nào.",
        reply_markup=markup,
    )


def _render_channel_pick_menu(bot, message, prefix, title, action_text):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in list_all_channels():
        markup.add(
            InlineKeyboardButton(
                text=f"{channel['title']} ({channel['key']})",
                callback_data=f"{prefix}:{channel['key']}"
            )
        )

    bot.send_message(
        message.chat.id,
        f"{title}\n\n{action_text}",
        reply_markup=markup,
    )


def register_handlers(bot):
    @bot.message_handler(commands=['notif', 'thongbao', 'tbnhom'])
    def notification_menu(message):
        if _deny_if_not_admin(message, bot):
            return
        log_user_action(message, "/notif", "Opened notification management")
        _render_menu(bot, message)

    @bot.message_handler(commands=['notiflist', 'dslnotif'])
    def notification_list(message):
        if _deny_if_not_admin(message, bot):
            return
        log_user_action(message, "/notiflist", "Listed notification channels")
        lines = ["📋 DANH SÁCH KÊNH THÔNG BÁO"]
        for channel in list_all_channels():
            lines.append(_format_channel_line(channel))
        bot.send_message(message.chat.id, "\n".join(lines))

    @bot.message_handler(commands=['notiflookup', 'notiffind'])
    def notification_lookup(message):
        if _deny_if_not_admin(message, bot):
            return
        log_user_action(message, "/notiflookup", "Opened chat ID lookup")
        _render_lookup_menu(bot, message)

    @bot.message_handler(commands=['notifadd', 'notifassign'])
    def notification_add_start(message):
        if _deny_if_not_admin(message, bot):
            return
        log_user_action(message, "/notifadd", "Opened add chat ID flow")
        _render_channel_pick_menu(
            bot,
            message,
            "notif:add",
            "➕ THÊM CHAT ID VÀO KÊNH",
            "Chọn kênh muốn gắn rồi gửi tiếp: /notifsetid <channel> <chat_id>"
        )

    @bot.message_handler(commands=['notifsetid'])
    def notification_set_id(message):
        if _deny_if_not_admin(message, bot):
            return

        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 3:
            bot.send_message(message.chat.id, "Dùng: /notifsetid <channel> <chat_id>")
            return

        channel_key = parts[1].strip()
        try:
            chat_id = int(parts[2].strip())
        except ValueError:
            bot.send_message(message.chat.id, "chat_id không hợp lệ.")
            return

        added = add_chat_id(channel_key, chat_id)
        bot.send_message(
            message.chat.id,
            f"{'Đã thêm' if added else 'Chat ID đã có sẵn'} {chat_id} vào {channel_key}."
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('notif:add:'))
    def handle_add_pick(call):
        if call.from_user.id != getattr(config, "ID_ADMIN", None):
            bot.answer_callback_query(call.id, "Bạn không có quyền dùng lệnh này", show_alert=True)
            return

        channel_key = call.data.split(':', 2)[2]
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"Đã chọn {channel_key}. Gửi tiếp: /notifsetid {channel_key} <chat_id>"
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('notif:toggle:'))
    def handle_toggle_callback(call):
        if call.from_user.id != getattr(config, "ID_ADMIN", None):
            bot.answer_callback_query(call.id, "Bạn không có quyền dùng lệnh này", show_alert=True)
            return

        channel_key = call.data.split(':', 2)[2]
        channel = get_channel_info(channel_key)
        new_state = not channel['enabled']
        set_channel_enabled(channel_key, new_state)
        bot.answer_callback_query(call.id, f"Đã {'bật' if new_state else 'tắt'} {channel_key}")
        _render_menu(bot, call.message)

    @bot.callback_query_handler(func=lambda call: call.data == 'notif:join_current')
    def handle_join_current(call):
        if call.from_user.id != getattr(config, "ID_ADMIN", None):
            bot.answer_callback_query(call.id, "Bạn không có quyền dùng lệnh này", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Dùng /notifadd để chọn kênh rồi nhập /notifsetid <channel> <chat_id>.")

    @bot.callback_query_handler(func=lambda call: call.data == 'notif:leave_current')
    def handle_leave_current(call):
        if call.from_user.id != getattr(config, "ID_ADMIN", None):
            bot.answer_callback_query(call.id, "Bạn không có quyền dùng lệnh này", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Dùng /notifwhere <chat_id> để xem chat đó đang gắn kênh nào, rồi dùng /notifremove <channel> <chat_id> để bỏ.")

    @bot.callback_query_handler(func=lambda call: call.data == 'notif:listdetail')
    def handle_listdetail(call):
        if call.from_user.id != getattr(config, "ID_ADMIN", None):
            bot.answer_callback_query(call.id, "Bạn không có quyền dùng lệnh này", show_alert=True)
            return

        lines = ["📋 KÊNH VÀ NHÓM ĐÃ GẮN"]
        for channel in list_all_channels():
            members = get_channel_members(channel["key"])
            member_text = ", ".join(str(item) for item in members) if members else "Không có nhóm nào"
            lines.append(f"• {channel['key']} | {channel['title']} | {member_text}")

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "\n".join(lines))

    @bot.callback_query_handler(func=lambda call: call.data == 'notif:lookup')
    def handle_lookup(call):
        if call.from_user.id != getattr(config, "ID_ADMIN", None):
            bot.answer_callback_query(call.id, "Bạn không có quyền dùng lệnh này", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "Gửi tiếp một chat ID theo dạng: /notifwhere <chat_id>"
        )

    @bot.message_handler(commands=['notifwhere'])
    def notification_where(message):
        if _deny_if_not_admin(message, bot):
            return

        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Dùng: /notifwhere <chat_id>")
            return

        try:
            chat_id = int(parts[1].strip())
        except ValueError:
            bot.send_message(message.chat.id, "chat_id không hợp lệ.")
            return

        assignments = find_chat_assignments(chat_id)
        if not assignments:
            bot.send_message(message.chat.id, f"{chat_id} hiện chưa gắn với kênh nào.")
            return

        lines = [f"🔎 CHAT ID {chat_id} ĐANG DÙNG CHO:"]
        for item in assignments:
            state = "BẬT" if item["enabled"] else "TẮT"
            lines.append(f"• {item['key']} | {item['title']} | {state}")

        bot.send_message(message.chat.id, "\n".join(lines))

    @bot.message_handler(commands=['notifremove', 'notifunassign'])
    def notification_remove(message):
        if _deny_if_not_admin(message, bot):
            return

        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 3:
            bot.send_message(message.chat.id, "Dùng: /notifremove <channel> <chat_id>")
            return

        channel_key = parts[1].strip()
        try:
            chat_id = int(parts[2].strip())
        except ValueError:
            bot.send_message(message.chat.id, "chat_id không hợp lệ.")
            return

        removed = remove_chat_id(channel_key, chat_id)
        bot.send_message(message.chat.id, f"{'Đã xóa' if removed else 'Không tìm thấy'} {chat_id} khỏi {channel_key}.")
