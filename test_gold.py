#!/usr/bin/env python3
"""
Test script for gold price storage functionality
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.json_storage import JSONStorage
import config

# Initialize gold price storage (same as in handlers/gold.py)
GOLD_PRICE_FILE = os.path.join(config.DATA_DIR, 'gold_prices.json')
gold_storage = JSONStorage(GOLD_PRICE_FILE, default_data={})

def get_previous_gold_price(gold_type):
    """Get the most recent saved gold price for comparison"""
    try:
        all_prices = gold_storage.load()
        
        if gold_type in all_prices and len(all_prices[gold_type]) > 0:
            latest = all_prices[gold_type][0]
            return {
                "buy": latest.get("buy"),
                "sell": latest.get("sell")
            }
        return None
    except Exception as e:
        print(f"Error getting previous gold price for {gold_type}: {str(e)}")
        return None

def get_price_indicator(current, previous):
    """Get color indicator based on price change"""
    if current is None or previous is None:
        return "⚪"  # White circle for no data
    
    if current > previous:
        return "🟢"  # Green - price increased
    elif current < previous:
        return "🔴"  # Red - price decreased
    else:
        return "🟡"  # Yellow - price unchanged

def save_gold_price(gold_type, buy_price, sell_price):
    """Save gold price data to history file"""
    try:
        all_prices = gold_storage.load()
        
        # Initialize gold type list if not exists
        if gold_type not in all_prices:
            all_prices[gold_type] = []
        
        # Create new entry with timestamp
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "buy": buy_price,
            "sell": sell_price
        }
        
        # Add to history (newest first)
        all_prices[gold_type].insert(0, new_entry)
        
        # Keep only last 100 entries per type to avoid file bloat
        all_prices[gold_type] = all_prices[gold_type][:100]
        
        # Save back to file
        gold_storage.save(all_prices)
        print(f"✅ Saved gold price: {gold_type} | Buy: {buy_price} | Sell: {sell_price}")
        
    except Exception as e:
        print(f"❌ Error saving gold price {gold_type}: {str(e)}")

def simulate_gold_price_request(gold_type, buy, sell):
    """Simulate a gold price request with comparison"""
    
    # Get previous price
    previous_price = get_previous_gold_price(gold_type)
    
    # Save new price
    save_gold_price(gold_type, buy, sell)
    
    # Get indicators
    buy_indicator = get_price_indicator(
        buy,
        previous_price['buy'] if previous_price else None
    )
    sell_indicator = get_price_indicator(
        sell,
        previous_price['sell'] if previous_price else None
    )
    
    # Format message
    msg = f"💰 {gold_type}\n"
    msg += f"{buy_indicator} Mua: {buy:,.3f} | {sell_indicator} Bán: {sell:,.3f}"
    
    # Add comparison if previous exists
    if previous_price:
        buy_change = buy - previous_price['buy']
        sell_change = sell - previous_price['sell']
        msg += "\n📊 So với lần trước:"
        
        if buy_change != 0:
            msg += f" Mua {'+' if buy_change > 0 else ''}{buy_change:,.3f}"
        if sell_change != 0:
            msg += f" | Bán {'+' if sell_change > 0 else ''}{sell_change:,.3f}"
        if buy_change == 0 and sell_change == 0:
            msg += " Không đổi"
    
    return msg

def main():
    print("=" * 70)
    print("TEST: Gold Price Storage & Comparison")
    print("=" * 70)
    
    # Test SJC gold
    print("\n👑 Testing SJC_MIENG:")
    print("-" * 70)
    
    print("\n🔵 Request 1: Lần đầu tiên")
    msg = simulate_gold_price_request('SJC_MIENG', 183.500, 184.800)
    print(msg)
    
    print("\n\n🟡 Request 2: Giá không đổi")
    msg = simulate_gold_price_request('SJC_MIENG', 183.500, 184.800)
    print(msg)
    
    print("\n\n🟢 Request 3: Giá tăng")
    msg = simulate_gold_price_request('SJC_MIENG', 184.000, 185.200)
    print(msg)
    
    print("\n\n🔴 Request 4: Giá giảm")
    msg = simulate_gold_price_request('SJC_MIENG', 183.200, 184.500)
    print(msg)
    
    # Test DOJI gold
    print("\n\n⚜️ Testing DOJI_NHAN:")
    print("-" * 70)
    
    print("\n🔵 Request 1: Lần đầu tiên")
    msg = simulate_gold_price_request('DOJI_NHAN', 90.500, 92.800)
    print(msg)
    
    print("\n\n🟢 Request 2: Giá tăng")
    msg = simulate_gold_price_request('DOJI_NHAN', 91.000, 93.200)
    print(msg)
    
    # Test world gold
    print("\n\n🌍 Testing WORLD_GOLD_USD:")
    print("-" * 70)
    
    print("\n🔵 Request 1: Lần đầu tiên")
    msg = simulate_gold_price_request('WORLD_GOLD_USD', 2950.50, 2950.50)
    print(msg)
    
    print("\n\n🔴 Request 2: Giá giảm")
    msg = simulate_gold_price_request('WORLD_GOLD_USD', 2920.30, 2920.30)
    print(msg)
    
    # Show saved data
    print("\n\n" + "=" * 70)
    print("📜 Saved Gold Price History:")
    print("=" * 70)
    
    try:
        with open(GOLD_PRICE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for gold_type, history in data.items():
            print(f"\n💰 {gold_type}:")
            for i, entry in enumerate(history[:3], 1):
                print(f"   {i}. {entry['timestamp']}")
                print(f"      Mua: {entry['buy']:,.3f} | Bán: {entry['sell']:,.3f}")
            
            if len(history) > 3:
                print(f"   ... ({len(history) - 3} more entries)")
    
    except FileNotFoundError:
        print("❌ Gold price file not found!")
    except json.JSONDecodeError as e:
        print(f"❌ Error reading JSON: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Test completed!")
    print(f"Data file: {GOLD_PRICE_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
