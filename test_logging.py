#!/usr/bin/env python3
"""
Test script để kiểm tra logging system
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.log_helper import log_user_action

# Mock message object để test
class MockUser:
    def __init__(self):
        self.id = 123456789
        self.username = "testuser"
        self.first_name = "Test"
        self.last_name = "User"

class MockChat:
    def __init__(self):
        self.id = 987654321
        self.type = "private"

class MockMessage:
    def __init__(self):
        self.from_user = MockUser()
        self.chat = MockChat()
        self.text = "/test command"

if __name__ == "__main__":
    print("🧪 Testing logging system...")
    
    # Tạo mock message
    message = MockMessage()
    
    # Test logging
    print("📝 Writing test log entries...")
    log_user_action(message, "/test", "This is a test log entry")
    log_user_action(message, "/stock", "Symbol: VCB")
    log_user_action(message, "/aug", "Requested gold price: both")
    
    print("✅ Log entries written successfully!")
    print("\n📋 Check the log file:")
    print("   tail -10 logs/bot_usage.log")
    
    # Đọc và hiển thị 5 dòng cuối của log
    try:
        with open('logs/bot_usage.log', 'r') as f:
            lines = f.readlines()
            print("\n📊 Last 5 log entries:")
            print("=" * 80)
            for line in lines[-5:]:
                print(line.rstrip())
            print("=" * 80)
    except Exception as e:
        print(f"⚠️  Could not read log file: {e}")
