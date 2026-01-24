import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logs.logs import setup_logger 
from get_api.taixiu import TaiXiuGame
from utils.log_helper import log_user_action
import json

taixiu_log = setup_logger('taixiu.log')
game = TaiXiuGame()

def register_handlers(bot):
    @bot.message_handler(commands=['taixiu'])
    def taixiu_handler(message):
        log_user_action(message, "/taixiu", "User started taixiu game")
        user_id = str(message.from_user.id)
        username = message.from_user.username or message.from_user.first_name
        
        try:
            # Kiểm tra và tạo tài khoản nếu chưa có
            user_info = game.get_or_create_user(user_id, username)
            points = user_info['points']
            
            if points <= 0:
                bot.send_message(
                    message.chat.id,
                    f"💸 Bạn đã hết điểm! Tài khoản của bạn sẽ được reset về 5000 điểm."
                )
                game.reset_user_points(user_id)
                points = 5000
            
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = [
                InlineKeyboardButton(text="🎲 TÀI (11-18)", callback_data=f"choice_tai_{user_id}"),
                InlineKeyboardButton(text="🎲 XỈU (3-10)", callback_data=f"choice_xiu_{user_id}"),
            ]
            markup.add(*buttons)
            
            bot.send_message(
                message.chat.id,
                f"🎰 **GAME TÀI XỈU VUI VẺ** 🎰\n\n"
                f"👤 Người chơi: {username}\n"
                f"💰 Điểm hiện tại: {points:,} điểm\n\n"
                f"🎯 Chọn TÀI hoặc XỈU:",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        except Exception as e:
            taixiu_log.error(f"Error in taixiu_handler: {e}")
            bot.send_message(message.chat.id, "❌ Có lỗi xảy ra, vui lòng thử lại!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("choice_"))
    def choose_bet_amount(call):
        try:
            _, choice, user_id = call.data.split("_")
            
            if str(call.from_user.id) != user_id:
                bot.answer_callback_query(call.id, "❌ Bạn không thể chọn cho người khác!")
                return
            
            user_info = game.get_user(user_id)
            if not user_info:
                bot.answer_callback_query(call.id, "❌ Không tìm thấy thông tin người chơi!")
                return
            
            points = user_info['points']
            choice_text = "TÀI (11-18)" if choice == "tai" else "XỈU (3-10)"
            
            markup = InlineKeyboardMarkup(row_width=2)
            bet_amounts = [100, 500, 1000, 2000, 5000]
            
            buttons = []
            for amount in bet_amounts:
                if amount <= points:
                    buttons.append(
                        InlineKeyboardButton(
                            text=f"{amount:,} điểm", 
                            callback_data=f"bet_{choice}_{amount}_{user_id}"
                        )
                    )
            
            # Thêm nút cược tất cả
            if points > 0:
                buttons.append(
                    InlineKeyboardButton(
                        text=f"ALL-IN ({points:,})", 
                        callback_data=f"bet_{choice}_{points}_{user_id}"
                    )
                )
            
            markup.add(*buttons)
            
            bot.edit_message_text(
                f"🎯 Bạn đã chọn: **{choice_text}**\n\n"
                f"💰 Điểm hiện tại: {points:,} điểm\n"
                f"💸 Chọn mức cược:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        except Exception as e:
            taixiu_log.error(f"Error in choose_bet_amount: {e}")
            bot.answer_callback_query(call.id, "❌ Có lỗi xảy ra!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("bet_"))
    def play_game(call):
        try:
            _, choice, bet_amount, user_id = call.data.split("_")
            bet_amount = int(bet_amount)
            
            if str(call.from_user.id) != user_id:
                bot.answer_callback_query(call.id, "❌ Bạn không thể chơi cho người khác!")
                return
            
            # Chơi game
            result = game.play(user_id, choice, bet_amount)
            
            if not result['success']:
                taixiu_log.warning(f"Game play failed: {result['message']} | User: {call.from_user.username} (ID: {user_id})")
                bot.answer_callback_query(call.id, f"❌ {result['message']}")
                return
            
            # Hiển thị kết quả
            dice1, dice2, dice3 = result['dice']
            total = result['total']
            win = result['win']
            new_points = result['new_points']
            choice_text = "TÀI" if choice == "tai" else "XIỦ"
            result_text = "TÀI" if total >= 11 else "XIỦ"
            
            # Log kết quả game
            taixiu_log.info(f"Game played: Choice={choice_text} | Bet={bet_amount} | Dice={dice1}+{dice2}+{dice3}={total} | Result={result_text} | Win={win} | NewPoints={new_points} | User: {call.from_user.username} (ID: {user_id})")
            
            win_emoji = "🎉" if win else "😢"
            result_emoji = "📈" if win else "📉"
            
            message = (
                f"🎲 **KẾT QUẢ TÀI XỈU** 🎲\n\n"
                f"🎯 Bạn chọn: **{choice_text}**\n"
                f"💸 Cược: {bet_amount:,} điểm\n\n"
                f"🎲 Kết quả xúc xắc: {dice1} + {dice2} + {dice3} = **{total}**\n"
                f"🎯 Kết quả: **{result_text}**\n\n"
                f"{win_emoji} {'THẮNG!' if win else 'THUA!'}\n"
                f"{result_emoji} Điểm mới: **{new_points:,}** điểm\n"
                f"({'+ ' + str(bet_amount) if win else '- ' + str(bet_amount)} điểm)"
            )
            
            # Tạo nút chơi lại
            markup = InlineKeyboardMarkup()
            if new_points > 0:
                markup.add(
                    InlineKeyboardButton(
                        text="🔄 Chơi lại", 
                        callback_data=f"play_again_{user_id}"
                    )
                )
            else:
                markup.add(
                    InlineKeyboardButton(
                        text="💰 Reset điểm", 
                        callback_data=f"reset_points_{user_id}"
                    )
                )
            
            bot.edit_message_text(
                message,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        except Exception as e:
            taixiu_log.error(f"Error in play_game: {e}")
            bot.answer_callback_query(call.id, "❌ Có lỗi xảy ra!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("play_again_"))
    def play_again(call):
        user_id = call.data.split("_")[2]
        
        if str(call.from_user.id) != user_id:
            bot.answer_callback_query(call.id, "❌ Bạn không thể chơi cho người khác!")
            return
        
        user_info = game.get_user(user_id)
        points = user_info['points']
        username = user_info['username']
        
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton(text="🎲 TÀI (11-18)", callback_data=f"choice_tai_{user_id}"),
            InlineKeyboardButton(text="🎲 XỈU (3-10)", callback_data=f"choice_xiu_{user_id}"),
        ]
        markup.add(*buttons)
        
        bot.edit_message_text(
            f"🎰 **GAME TÀI XỈU VUI VẺ** 🎰\n\n"
            f"👤 Người chơi: {username}\n"
            f"💰 Điểm hiện tại: {points:,} điểm\n\n"
            f"🎯 Chọn TÀI hoặc XỈU:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reset_points_"))
    def reset_points(call):
        user_id = call.data.split("_")[2]
        
        if str(call.from_user.id) != user_id:
            bot.answer_callback_query(call.id, "❌ Bạn không thể reset cho người khác!")
            return
        
        game.reset_user_points(user_id)
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                text="🎮 Bắt đầu chơi", 
                callback_data=f"play_again_{user_id}"
            )
        )
        
        bot.edit_message_text(
            f"💰 **RESET ĐIỂM THÀNH CÔNG!** 💰\n\n"
            f"🎁 Bạn được tặng: **5,000 điểm**\n"
            f"🎮 Chúc bạn may mắn!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    @bot.message_handler(commands=['taixiustats', 'statx'])
    def show_stats(message):
        log_user_action(message, "/taixiustats", "User requested taixiu statistics")
        user_id = str(message.from_user.id)
        
        try:
            stats = game.get_user_stats(user_id)
            if not stats:
                taixiu_log.info(f"Stats requested but user has no games | User: {message.from_user.username} (ID: {user_id})")
                bot.send_message(
                    message.chat.id,
                    "❌ Bạn chưa chơi game tài xỉu lần nào!\n"
                    "📝 Gõ /taixiu để bắt đầu chơi."
                )
                return
            
            message_text = (
                f"📊 **THỐNG KÊ TÀI XỈU** 📊\n\n"
                f"👤 **Người chơi:** {stats['username']}\n"
                f"💰 **Điểm hiện tại:** {stats['points']:,} điểm\n\n"
                f"🎮 **Tổng số ván:** {stats['total_games']}\n"
                f"🏆 **Số ván thắng:** {stats['wins']}\n"
                f"💸 **Số ván thua:** {stats['losses']}\n"
                f"📈 **Tỷ lệ thắng:** {stats['win_rate']:.1f}%\n\n"
                f"📅 **Lần chơi cuối:** {stats['last_played'][:10]}"
            )
            
            taixiu_log.info(f"Stats displayed: Games={stats['total_games']} | Wins={stats['wins']} | WinRate={stats['win_rate']:.1f}% | Points={stats['points']} | User: {stats['username']} (ID: {user_id})")
            
            bot.send_message(
                message.chat.id,
                message_text,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            taixiu_log.error(f"Error in show_stats: {e}")
            bot.send_message(message.chat.id, "❌ Có lỗi xảy ra khi lấy thống kê!")
