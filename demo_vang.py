#!/usr/bin/env python3
"""
Demo: Simulate /vang command output with real data
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_api.gold import get_gold, URL_SJC, URL_DOJI, make_gold_XAUUSD_request
from get_api.usd import get_vcb_exchange_rate
from test_gold import (
    get_previous_gold_price,
    get_price_indicator,
    save_gold_price
)

def extract_price_number(price_str):
    """Extract numeric price from formatted strings"""
    try:
        price_part = price_str.split('x1000')[0].strip()
        price_part = price_part.replace(',', '').replace('.', '').strip()
        return float(price_part) / 1000
    except:
        return 0

def simulate_vang_command():
    """Simulate the /vang command output"""
    
    print("=" * 70)
    print("DEMO: /vang Command Output")
    print("=" * 70)
    print()
    
    try:
        # Get SJC and DOJI prices
        gold_sjc = get_gold(URL_SJC)
        gold_doji = get_gold(URL_DOJI)
        
        # Extract numeric prices
        sjc_buy = extract_price_number(gold_sjc['vang_mieng']['mua'])
        sjc_sell = extract_price_number(gold_sjc['vang_mieng']['ban'])
        doji_buy = extract_price_number(gold_doji['vang_nhan']['mua'])
        doji_sell = extract_price_number(gold_doji['vang_nhan']['ban'])
        
        # Get previous prices BEFORE saving new ones
        prev_sjc = get_previous_gold_price('SJC_MIENG')
        prev_doji = get_previous_gold_price('DOJI_NHAN')
        
        # Save new prices to history
        save_gold_price('SJC_MIENG', sjc_buy, sjc_sell)
        save_gold_price('DOJI_NHAN', doji_buy, doji_sell)
        
        # Get price indicators
        sjc_buy_indicator = get_price_indicator(sjc_buy, prev_sjc['buy'] if prev_sjc else None)
        sjc_sell_indicator = get_price_indicator(sjc_sell, prev_sjc['sell'] if prev_sjc else None)
        doji_buy_indicator = get_price_indicator(doji_buy, prev_doji['buy'] if prev_doji else None)
        doji_sell_indicator = get_price_indicator(doji_sell, prev_doji['sell'] if prev_doji else None)
        
        # Get world gold price
        price_usd = make_gold_XAUUSD_request()
        usd_rate = get_vcb_exchange_rate("USD")
        
        msg = ""
        if price_usd and usd_rate and usd_rate['sell']:
            # Convert USD/oz to VND/lượng
            oz_to_luong = 37.5 / 31.1035
            price_vnd_per_luong = price_usd * usd_rate['sell'] * oz_to_luong
            
            # Calculate difference with SJC sell price
            diff = (sjc_sell * 1_000_000) - price_vnd_per_luong
            diff_icon = "📈" if diff > 0 else "📉"
            
            msg += f"🌏 Giá TG: {price_usd:,.2f} USD/oz\n"
            msg += f"🏦 Tỷ giá bank: {usd_rate['sell']:,.0f} → Giá Hiện tại: {price_vnd_per_luong:,.0f} VND\n"
            msg += f"🏅 Chênh lệch với SJC: {diff_icon} {abs(diff):,.0f} VND\n\n"
        
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += f"👑 Miếng SJC: {sjc_buy_indicator} {sjc_buy:,.3f} - {sjc_sell_indicator} {sjc_sell:,.3f}\n"
        msg += f"⚜️ Doji: {doji_buy_indicator} {doji_buy:,.3f} - {doji_sell_indicator} {doji_sell:,.3f}"
        
        # Add price change info if there's previous data
        if prev_sjc or prev_doji:
            msg += "\n\n📊 _So với lần trước:_"
            
            if prev_sjc:
                sjc_buy_change = sjc_buy - prev_sjc['buy']
                sjc_sell_change = sjc_sell - prev_sjc['sell']
                msg += f"\n👑 SJC:"
                if sjc_buy_change != 0:
                    msg += f" Mua {'+' if sjc_buy_change > 0 else ''}{sjc_buy_change:,.3f}"
                if sjc_sell_change != 0:
                    msg += f" | Bán {'+' if sjc_sell_change > 0 else ''}{sjc_sell_change:,.3f}"
                if sjc_buy_change == 0 and sjc_sell_change == 0:
                    msg += " Không đổi"
            
            if prev_doji:
                doji_buy_change = doji_buy - prev_doji['buy']
                doji_sell_change = doji_sell - prev_doji['sell']
                msg += f"\n⚜️ Doji:"
                if doji_buy_change != 0:
                    msg += f" Mua {'+' if doji_buy_change > 0 else ''}{doji_buy_change:,.3f}"
                if doji_sell_change != 0:
                    msg += f" | Bán {'+' if doji_sell_change > 0 else ''}{doji_sell_change:,.3f}"
                if doji_buy_change == 0 and doji_sell_change == 0:
                    msg += " Không đổi"
        
        print(msg)
        
    except Exception as e:
        print(f"❌ Lỗi khi lấy giá vàng: {str(e)}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    simulate_vang_command()
