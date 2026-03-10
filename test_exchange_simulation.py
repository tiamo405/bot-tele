#!/usr/bin/env python3
"""
Test script to simulate multiple exchange rate requests with changing prices
"""
import os
import sys
import json
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.exchange_rate import (
    save_exchange_rate, 
    get_previous_rate, 
    get_price_indicator,
    EXCHANGE_RATE_FILE
)

def simulate_bot_response(currency, buy, sell):
    """Simulate bot response for /tigia command"""
    
    # Prepare rate data
    rate_data = {
        "currency": currency,
        "buy": buy,
        "sell": sell,
        "source": "Vietcombank"
    }
    
    # Get previous rate
    previous_rate = get_previous_rate(currency)
    
    # Save new rate
    save_exchange_rate(rate_data)
    
    # Get indicators
    buy_indicator = get_price_indicator(
        rate_data['buy'],
        previous_rate['buy'] if previous_rate else None
    )
    sell_indicator = get_price_indicator(
        rate_data['sell'],
        previous_rate['sell'] if previous_rate else None
    )
    
    # Format message
    msg = f"💱 *Tỷ giá {rate_data['currency']}*\n\n"
    msg += f"{buy_indicator} Mua vào: *{rate_data['buy']:,.0f} VND*\n"
    msg += f"{sell_indicator} Bán ra: *{rate_data['sell']:,.0f} VND*\n"
    msg += f"\n_Nguồn: {rate_data['source']}_"
    
    # Add comparison if previous data exists
    if previous_rate:
        msg += "\n\n📊 _So với lần trước:_"
        
        buy_change = rate_data['buy'] - previous_rate['buy']
        if buy_change > 0:
            msg += f"\n• Mua: +{buy_change:,.0f} VND"
        elif buy_change < 0:
            msg += f"\n• Mua: {buy_change:,.0f} VND"
        else:
            msg += f"\n• Mua: Không đổi"
        
        sell_change = rate_data['sell'] - previous_rate['sell']
        if sell_change > 0:
            msg += f"\n• Bán: +{sell_change:,.0f} VND"
        elif sell_change < 0:
            msg += f"\n• Bán: {sell_change:,.0f} VND"
        else:
            msg += f"\n• Bán: Không đổi"
    
    return msg

def main():
    print("=" * 70)
    print("SIMULATION: Multiple /tigia Requests with Price Changes")
    print("=" * 70)
    
    # Scenario 1: First request - no previous data
    print("\n🔵 Request 1: Lần đầu tiên")
    print("-" * 70)
    msg = simulate_bot_response("CNY", 3600.0, 3650.0)
    print(msg)
    time.sleep(0.5)
    
    # Scenario 2: Price stays same
    print("\n\n🟡 Request 2: Giá không đổi")
    print("-" * 70)
    msg = simulate_bot_response("CNY", 3600.0, 3650.0)
    print(msg)
    time.sleep(0.5)
    
    # Scenario 3: Price increases
    print("\n\n🟢 Request 3: Giá tăng")
    print("-" * 70)
    msg = simulate_bot_response("CNY", 3620.0, 3680.0)
    print(msg)
    time.sleep(0.5)
    
    # Scenario 4: Price decreases
    print("\n\n🔴 Request 4: Giá giảm")
    print("-" * 70)
    msg = simulate_bot_response("CNY", 3590.0, 3640.0)
    print(msg)
    time.sleep(0.5)
    
    # Scenario 5: Mixed changes (buy up, sell down)
    print("\n\n🟠 Request 5: Biến động hỗn hợp (Mua tăng, Bán giảm)")
    print("-" * 70)
    msg = simulate_bot_response("CNY", 3610.0, 3620.0)
    print(msg)
    
    # Show history
    print("\n\n" + "=" * 70)
    print("📜 Lịch sử CNY trong file:")
    print("=" * 70)
    
    try:
        with open(EXCHANGE_RATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "CNY" in data:
            for i, entry in enumerate(data["CNY"][:5], 1):
                print(f"\n{i}. {entry['timestamp']}")
                print(f"   Mua: {entry['buy']:,.0f} | Bán: {entry['sell']:,.0f}")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Simulation completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
