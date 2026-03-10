#!/usr/bin/env python3
"""
Test script to demonstrate real gold price display with color indicators
"""
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_api.gold import get_gold, URL_SJC, URL_DOJI, make_gold_XAUUSD_request
from test_gold import (
    get_previous_gold_price,
    get_price_indicator,
    save_gold_price,
    GOLD_PRICE_FILE
)

def extract_price_number(price_str):
    """Extract numeric price from formatted strings"""
    try:
        price_part = price_str.split('x1000')[0].strip()
        price_part = price_part.replace(',', '').replace('.', '').strip()
        return float(price_part) / 1000
    except:
        return 0

def test_real_gold_prices():
    """Test with real gold prices from API"""
    
    print("=" * 70)
    print("TEST: Real Gold Prices with Color Indicators")
    print("=" * 70)
    
    try:
        # Get SJC prices
        print("\n👑 Fetching SJC prices...")
        gold_sjc = get_gold(URL_SJC)
        sjc_buy = extract_price_number(gold_sjc['vang_mieng']['mua'])
        sjc_sell = extract_price_number(gold_sjc['vang_mieng']['ban'])
        print(f"   ✅ SJC: Mua {sjc_buy:,.3f} | Bán {sjc_sell:,.3f}")
        
        # Get previous and save
        prev_sjc = get_previous_gold_price('SJC_MIENG')
        save_gold_price('SJC_MIENG', sjc_buy, sjc_sell)
        
        # Display with indicators
        sjc_buy_indicator = get_price_indicator(sjc_buy, prev_sjc['buy'] if prev_sjc else None)
        sjc_sell_indicator = get_price_indicator(sjc_sell, prev_sjc['sell'] if prev_sjc else None)
        
        print("\n📊 Display:")
        print(f"👑 Miếng SJC: {sjc_buy_indicator} {sjc_buy:,.3f} - {sjc_sell_indicator} {sjc_sell:,.3f}")
        
        if prev_sjc:
            sjc_buy_change = sjc_buy - prev_sjc['buy']
            sjc_sell_change = sjc_sell - prev_sjc['sell']
            print(f"📊 So với lần trước:", end="")
            if sjc_buy_change != 0:
                print(f" Mua {'+' if sjc_buy_change > 0 else ''}{sjc_buy_change:,.3f}", end="")
            if sjc_sell_change != 0:
                print(f" | Bán {'+' if sjc_sell_change > 0 else ''}{sjc_sell_change:,.3f}", end="")
            if sjc_buy_change == 0 and sjc_sell_change == 0:
                print(" Không đổi", end="")
            print()
        
    except Exception as e:
        print(f"   ❌ Error getting SJC: {e}")
    
    # Test DOJI
    try:
        print("\n⚜️ Fetching DOJI prices...")
        gold_doji = get_gold(URL_DOJI)
        doji_buy = extract_price_number(gold_doji['vang_nhan']['mua'])
        doji_sell = extract_price_number(gold_doji['vang_nhan']['ban'])
        print(f"   ✅ DOJI: Mua {doji_buy:,.3f} | Bán {doji_sell:,.3f}")
        
        # Get previous and save
        prev_doji = get_previous_gold_price('DOJI_NHAN')
        save_gold_price('DOJI_NHAN', doji_buy, doji_sell)
        
        # Display with indicators
        doji_buy_indicator = get_price_indicator(doji_buy, prev_doji['buy'] if prev_doji else None)
        doji_sell_indicator = get_price_indicator(doji_sell, prev_doji['sell'] if prev_doji else None)
        
        print("\n📊 Display:")
        print(f"⚜️ Doji: {doji_buy_indicator} {doji_buy:,.3f} - {doji_sell_indicator} {doji_sell:,.3f}")
        
        if prev_doji:
            doji_buy_change = doji_buy - prev_doji['buy']
            doji_sell_change = doji_sell - prev_doji['sell']
            print(f"📊 So với lần trước:", end="")
            if doji_buy_change != 0:
                print(f" Mua {'+' if doji_buy_change > 0 else ''}{doji_buy_change:,.3f}", end="")
            if doji_sell_change != 0:
                print(f" | Bán {'+' if doji_sell_change > 0 else ''}{doji_sell_change:,.3f}", end="")
            if doji_buy_change == 0 and doji_sell_change == 0:
                print(" Không đổi", end="")
            print()
        
    except Exception as e:
        print(f"   ❌ Error getting DOJI: {e}")
    
    # Test World Gold
    try:
        print("\n🌍 Fetching world gold price...")
        price_usd = make_gold_XAUUSD_request()
        
        if price_usd:
            print(f"   ✅ World: ${price_usd:,.2f}/oz")
            
            # Get previous and save
            prev_world = get_previous_gold_price('WORLD_GOLD_USD')
            save_gold_price('WORLD_GOLD_USD', price_usd, price_usd)
            
            # Display with indicator
            price_indicator = get_price_indicator(price_usd, prev_world['buy'] if prev_world else None)
            
            print("\n📊 Display:")
            print(f"🌐 Giá vàng thế giới: {price_indicator} ${price_usd:,.2f}/oz")
            
            if prev_world and prev_world['buy']:
                price_change = price_usd - prev_world['buy']
                print(f"📊 So với lần trước:", end="")
                if price_change > 0:
                    print(f" +${price_change:,.2f}/oz")
                elif price_change < 0:
                    print(f" ${price_change:,.2f}/oz")
                else:
                    print(" Không đổi")
        else:
            print("   ❌ Could not get world gold price")
            
    except Exception as e:
        print(f"   ❌ Error getting world gold: {e}")
    
    # Show history
    print("\n" + "=" * 70)
    print("📜 Gold Price History (Last 3 entries):")
    print("=" * 70)
    
    try:
        with open(GOLD_PRICE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for gold_type, history in data.items():
            print(f"\n💰 {gold_type}:")
            for i, entry in enumerate(history[:3], 1):
                print(f"   {i}. {entry['timestamp']}: Mua {entry['buy']:,.3f} | Bán {entry['sell']:,.3f}")
    
    except Exception as e:
        print(f"Error reading history: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Test completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_real_gold_prices()
