#!/usr/bin/env python3
"""
Test script to demonstrate exchange rate display with color indicators
"""
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.exchange_rate import get_previous_rate, get_price_indicator, EXCHANGE_RATE_FILE

def simulate_exchange_display(currency, current_buy, current_sell):
    """Simulate how the exchange rate would be displayed"""
    
    # Get previous rate
    previous_rate = get_previous_rate(currency)
    
    # Determine indicators
    buy_indicator = get_price_indicator(
        current_buy,
        previous_rate['buy'] if previous_rate else None
    )
    sell_indicator = get_price_indicator(
        current_sell,
        previous_rate['sell'] if previous_rate else None
    )
    
    # Format message
    msg = f"💱 *Tỷ giá {currency}*\n\n"
    
    if current_buy is not None:
        msg += f"{buy_indicator} Mua vào: *{current_buy:,.0f} VND*\n"
    else:
        msg += f"⚪ Mua vào: *-*\n"
    
    if current_sell is not None:
        msg += f"{sell_indicator} Bán ra: *{current_sell:,.0f} VND*\n"
    else:
        msg += f"⚪ Bán ra: *-*\n"
    
    msg += f"\n_Nguồn: Vietcombank_"
    
    # Add price change info
    if previous_rate:
        msg += "\n\n📊 _So với lần trước:_"
        if previous_rate['buy'] and current_buy:
            buy_change = current_buy - previous_rate['buy']
            if buy_change > 0:
                msg += f"\n• Mua: +{buy_change:,.0f} VND"
            elif buy_change < 0:
                msg += f"\n• Mua: {buy_change:,.0f} VND"
            else:
                msg += f"\n• Mua: Không đổi"
        
        if previous_rate['sell'] and current_sell:
            sell_change = current_sell - previous_rate['sell']
            if sell_change > 0:
                msg += f"\n• Bán: +{sell_change:,.0f} VND"
            elif sell_change < 0:
                msg += f"\n• Bán: {sell_change:,.0f} VND"
            else:
                msg += f"\n• Bán: Không đổi"
    
    return msg

def main():
    print("=" * 60)
    print("DEMO: Exchange Rate Display with Color Indicators")
    print("=" * 60)
    
    # Test 1: Same price (should show yellow circles)
    print("\n📋 Test 1: Giá không đổi (🟡)")
    print("-" * 60)
    msg = simulate_exchange_display("USD", 26041.0, 26311.0)
    print(msg)
    
    # Test 2: Price increase (manually change data to simulate)
    print("\n\n📋 Test 2: Giá tăng (🟢)")
    print("-" * 60)
    msg = simulate_exchange_display("USD", 26100.0, 26400.0)
    print(msg)
    
    # Test 3: Price decrease
    print("\n\n📋 Test 3: Giá giảm (🔴)")
    print("-" * 60)
    msg = simulate_exchange_display("USD", 26000.0, 26250.0)
    print(msg)
    
    # Test 4: No previous data (first time)
    print("\n\n📋 Test 4: Lần đầu tiên (⚪)")
    print("-" * 60)
    msg = simulate_exchange_display("CNY", 3600.0, 3650.0)
    print(msg)
    
    print("\n" + "=" * 60)
    print("Legend:")
    print("  🟢 = Giá tăng (Green)")
    print("  🔴 = Giá giảm (Red)")
    print("  🟡 = Giá không đổi (Yellow)")
    print("  ⚪ = Chưa có dữ liệu trước (White)")
    print("=" * 60)

if __name__ == "__main__":
    main()
