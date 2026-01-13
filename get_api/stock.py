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
            "color": str  # "green", "red", hoặc "yellow"
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
        
        # Tính phần trăm thay đổi
        change_percent = 0
        color = "yellow"  # Không đổi
        
        if current_price and reference_price:
            change_percent = ((current_price - reference_price) / reference_price) * 100
            if change_percent > 0:
                color = "green"
            elif change_percent < 0:
                color = "red"

        return {
            "symbol": row["listing_symbol"],
            "ceiling_price": row["listing_ceiling"], # giá trần
            "floor_price": row["listing_floor"], # giá sàn
            "reference_price": reference_price, # giá tham chiếu
            "current_price": current_price, # giá hiện tại
            "change_percent": change_percent,
            "color": color
        }
    except Exception as e:
        print(f"Error getting stock info for {symbol}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    info = get_stock_info("VNM")

    if info:
        for k, v in info.items():
            print(f"{k}: {v}")
    else:
        print("Không lấy được dữ liệu")
