from vnstock import Vnstock

def get_stock_info(symbol: str):
    """
    Lấy thông tin giá chứng khoán
    
    Returns:
        dict hoặc None: {
            "symbol": str,
            "ceiling_price": float,
            "floor_price": float,
            "reference_price": float,
            "current_price": float,
            "change_percent": float,  # % thay đổi so với giá tham chiếu
            "color": str  # "purple" (trần), "cyan" (sàn), "green" (tăng), "yellow" (tham chiếu), "red" (giảm)
        }
    """
    try:
        stock = Vnstock().stock(symbol=symbol.upper(), source="VCI")
        df = stock.trading.price_board([symbol])

        if df is None or df.empty:
            return None

        df.columns = ['_'.join(col) for col in df.columns]
        row = df.iloc[0]
        
        current_price = row.get("match_match_price")
        reference_price = row["listing_ref_price"]
        ceiling_price = row["listing_ceiling"]
        floor_price = row["listing_floor"]
        
        # Tính phần trăm thay đổi
        change_percent = 0
        color = "yellow"  # Không đổi (bằng giá tham chiếu)
        
        if current_price and reference_price:
            change_percent = ((current_price - reference_price) / reference_price) * 100
            
            # Xác định màu theo quy tắc thị trường VN:
            # - Tím (purple): Giá trần
            # - Xanh dương (cyan): Giá sàn
            # - Xanh lá (green): Tăng giá (> tham chiếu)
            # - Vàng (yellow): Không đổi (= tham chiếu)
            # - Đỏ (red): Giảm giá (< tham chiếu)
            
            if current_price >= ceiling_price:
                color = "purple"  # Giá trần
            elif current_price <= floor_price:
                color = "cyan"  # Giá sàn
            elif current_price > reference_price:
                color = "green"  # Tăng giá
            elif current_price < reference_price:
                color = "red"  # Giảm giá
            else:
                color = "yellow"  # Bằng tham chiếu

        return {
            "symbol": row["listing_symbol"],
            "ceiling_price": ceiling_price, # giá trần
            "floor_price": floor_price, # giá sàn
            "reference_price": reference_price, # giá tham chiếu
            "current_price": current_price, # giá hiện tại
            "change_percent": change_percent,
            "color": color  # "purple", "green", "yellow", "red", "cyan"
        }
    except Exception as e:
        print(f"Error getting stock info for {symbol}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Test với nhiều mã để xem các màu khác nhau
    test_symbols = ["PVC"]
    
    print("=== KIỂM TRA MÀU SẮC CÁC MÃ ===\n")
    for symbol in test_symbols:
        info = get_stock_info(symbol)
        if info:
            print(f"Mã: {info['symbol']}")
            print(f"  Giá trần: {info['ceiling_price']:,}")
            print(f"  Giá sàn: {info['floor_price']:,}")
            print(f"  Giá tham chiếu: {info['reference_price']:,}")
            print(f"  Giá hiện tại: {info['current_price']:,}")
            print(f"  Thay đổi: {info['change_percent']:.2f}%")
            print(f"  Màu: {info['color']}")
            print()
        else:
            print(f"Không lấy được dữ liệu cho {symbol}\n")
