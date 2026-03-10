#!/usr/bin/env python3
"""
Test script for exchange rate storage functionality
"""
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_api.usd import get_vcb_exchange_rate
from handlers.exchange_rate import save_exchange_rate, EXCHANGE_RATE_FILE

def test_exchange_rate_storage():
    """Test fetching and saving exchange rates"""
    
    print("=" * 60)
    print("Testing Exchange Rate Storage")
    print("=" * 60)
    
    # Test currencies
    currencies = ["USD", "EUR", "JPY", "GBP"]
    
    for currency in currencies:
        print(f"\n📊 Testing {currency}...")
        try:
            # Get exchange rate
            rate_data = get_vcb_exchange_rate(currency)
            
            if rate_data is None:
                print(f"   ❌ No data found for {currency}")
                continue
            
            print(f"   ✅ Fetched: Buy={rate_data['buy']}, Sell={rate_data['sell']}")
            
            # Save to file
            save_exchange_rate(rate_data)
            print(f"   ✅ Saved to {EXCHANGE_RATE_FILE}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Display saved data
    print("\n" + "=" * 60)
    print("Saved Exchange Rate Data:")
    print("=" * 60)
    
    try:
        with open(EXCHANGE_RATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for currency, history in data.items():
            print(f"\n💱 {currency}:")
            for i, entry in enumerate(history[:3]):  # Show last 3 entries
                print(f"   {i+1}. {entry['timestamp']}")
                print(f"      Buy: {entry['buy']}")
                print(f"      Sell: {entry['sell']}")
                print(f"      Source: {entry['source']}")
            
            if len(history) > 3:
                print(f"   ... ({len(history) - 3} more entries)")
    
    except FileNotFoundError:
        print("❌ Exchange rate file not found!")
    except json.JSONDecodeError as e:
        print(f"❌ Error reading JSON: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print(f"Data file location: {EXCHANGE_RATE_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    test_exchange_rate_storage()
