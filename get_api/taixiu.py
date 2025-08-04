import json
import random
import os
from datetime import datetime

class TaiXiuGame:
    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'taixiu_users.json')
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Đảm bảo file dữ liệu tồn tại"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def load_users(self):
        """Load dữ liệu người dùng từ file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_users(self, users_data):
        """Lưu dữ liệu người dùng vào file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users data: {e}")
            return False
    
    def get_or_create_user(self, user_id, username):
        """Lấy thông tin người dùng hoặc tạo mới nếu chưa có"""
        users = self.load_users()
        
        if user_id not in users:
            # Tạo người dùng mới với 5000 điểm
            users[user_id] = {
                'username': username,
                'points': 5000,
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'created_at': datetime.now().isoformat(),
                'last_played': datetime.now().isoformat()
            }
            self.save_users(users)
        else:
            # Cập nhật username nếu có thay đổi
            users[user_id]['username'] = username
            users[user_id]['last_played'] = datetime.now().isoformat()
            self.save_users(users)
        
        return users[user_id]
    
    def get_user(self, user_id):
        """Lấy thông tin người dùng"""
        users = self.load_users()
        return users.get(user_id)
    
    def update_user_points(self, user_id, new_points, win, bet_amount):
        """Cập nhật điểm người dùng"""
        users = self.load_users()
        if user_id in users:
            users[user_id]['points'] = new_points
            users[user_id]['total_games'] += 1
            users[user_id]['last_played'] = datetime.now().isoformat()
            
            if win:
                users[user_id]['wins'] += 1
            else:
                users[user_id]['losses'] += 1
            
            # Lưu lịch sử game (tùy chọn)
            if 'game_history' not in users[user_id]:
                users[user_id]['game_history'] = []
            
            users[user_id]['game_history'].append({
                'timestamp': datetime.now().isoformat(),
                'bet_amount': bet_amount,
                'win': win,
                'points_after': new_points
            })
            
            # Giới hạn lịch sử chỉ giữ 50 game gần nhất
            if len(users[user_id]['game_history']) > 50:
                users[user_id]['game_history'] = users[user_id]['game_history'][-50:]
            
            return self.save_users(users)
        return False
    
    def reset_user_points(self, user_id):
        """Reset điểm người dùng về 5000"""
        users = self.load_users()
        if user_id in users:
            users[user_id]['points'] = 5000
            users[user_id]['last_played'] = datetime.now().isoformat()
            return self.save_users(users)
        return False
    
    def roll_dice(self):
        """Tung 3 xúc xắc và trả về kết quả"""
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6) 
        dice3 = random.randint(1, 6)
        total = dice1 + dice2 + dice3
        return dice1, dice2, dice3, total
    
    def check_win(self, choice, total):
        """Kiểm tra thắng thua dựa trên lựa chọn và tổng điểm"""
        if choice == "tai":
            return total >= 11  # TÀI: 11-18
        else:  # choice == "xiu"
            return total <= 10  # XỈU: 3-10
    
    def play(self, user_id, choice, bet_amount):
        """Chơi một ván tài xỉu"""
        try:
            # Kiểm tra người dùng tồn tại
            user_info = self.get_user(user_id)
            if not user_info:
                return {
                    'success': False,
                    'message': 'Không tìm thấy thông tin người chơi!'
                }
            
            current_points = user_info['points']
            
            # Kiểm tra đủ điểm để cược
            if bet_amount > current_points:
                return {
                    'success': False,
                    'message': f'Không đủ điểm! Bạn chỉ có {current_points:,} điểm.'
                }
            
            if bet_amount <= 0:
                return {
                    'success': False,
                    'message': 'Mức cược phải lớn hơn 0!'
                }
            
            # Tung xúc xắc
            dice1, dice2, dice3, total = self.roll_dice()
            
            # Kiểm tra thắng thua
            win = self.check_win(choice, total)
            
            # Tính điểm mới
            if win:
                new_points = current_points + bet_amount
            else:
                new_points = current_points - bet_amount
            
            # Cập nhật điểm
            success = self.update_user_points(user_id, new_points, win, bet_amount)
            
            if not success:
                return {
                    'success': False,
                    'message': 'Có lỗi khi cập nhật điểm!'
                }
            
            return {
                'success': True,
                'dice': (dice1, dice2, dice3),
                'total': total,
                'win': win,
                'bet_amount': bet_amount,
                'old_points': current_points,
                'new_points': new_points
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Có lỗi xảy ra: {str(e)}'
            }
    
    def get_user_stats(self, user_id):
        """Lấy thống kê người dùng"""
        user_info = self.get_user(user_id)
        if not user_info:
            return None
        
        total_games = user_info.get('total_games', 0)
        wins = user_info.get('wins', 0)
        losses = user_info.get('losses', 0)
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        return {
            'username': user_info['username'],
            'points': user_info['points'],
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'created_at': user_info.get('created_at', ''),
            'last_played': user_info.get('last_played', '')
        }
