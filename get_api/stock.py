from vnstock import Vnstock
import requests
import sys
import os
from typing import Dict, List, Optional
from functools import lru_cache
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.retry_decorator import retry_on_exception


class StockAPI:
    """
    Singleton class để quản lý API chứng khoán với connection pooling và caching
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StockAPI, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Vnstock instance
        self.vnstock = Vnstock()
        
        # Requests session với connection pooling
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Cache config
        self.cache_ttl = 10  # Cache 10 giây để tránh spam API
        self.last_cache_time = {}
        self.cache = {}
        
        # API config
        self.vci_timeout = 10
        self.vietcap_url = "https://trading.vietcap.com.vn/api/price/v1/w/priceboard/tickers/price"
        
        self._initialized = True
    
    def _is_cache_valid(self, key: str) -> bool:
        """Kiểm tra cache còn hợp lệ không"""
        if key not in self.last_cache_time:
            return False
        return (time.time() - self.last_cache_time[key]) < self.cache_ttl
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Lấy data từ cache nếu còn hợp lệ"""
        if self._is_cache_valid(key):
            return self.cache.get(key)
        return None
    
    def _set_cache(self, key: str, value: Dict):
        """Lưu vào cache"""
        self.cache[key] = value
        self.last_cache_time[key] = time.time()
    
    def _calculate_stock_color(self, current: float, reference: float, ceiling: float, floor: float) -> str:
        """Tính màu của mã chứng khoán theo quy tắc VN"""
        if not current or not reference:
            return "yellow"
        
        if current >= ceiling:
            return "purple"  # Giá trần
        elif current <= floor:
            return "cyan"  # Giá sàn
        elif current > reference:
            return "green"  # Tăng giá
        elif current < reference:
            return "red"  # Giảm giá
        else:
            return "yellow"  # Tham chiếu
    
    @retry_on_exception(max_retries=2, delay=0.5, exceptions=(Exception,))
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Lấy thông tin 1 mã chứng khoán từ VCI
        
        Args:
            symbol: Mã chứng khoán (VD: VCB, FPT)
        
        Returns:
            Dict chứa thông tin stock hoặc None nếu lỗi
        """
        symbol = symbol.upper()
        
        # Check cache
        cache_key = f"single_{symbol}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            stock = self.vnstock.stock(symbol=symbol, source="VCI")
            df = stock.trading.price_board([symbol])

            if df is None or df.empty:
                return None

            df.columns = ['_'.join(col) for col in df.columns]
            row = df.iloc[0]
            
            current_price = row.get("match_match_price")
            reference_price = row["listing_ref_price"]
            ceiling_price = row["listing_ceiling"]
            floor_price = row["listing_floor"]
            name_company = row["listing_organ_name"]

            # Tính phần trăm thay đổi và màu
            change_percent = 0
            if current_price and reference_price:
                change_percent = ((current_price - reference_price) / reference_price) * 100
            
            color = self._calculate_stock_color(current_price, reference_price, ceiling_price, floor_price)

            result = {
                "symbol": row["listing_symbol"],
                "name_company": name_company,
                "ceiling_price": ceiling_price,
                "floor_price": floor_price,
                "reference_price": reference_price,
                "current_price": current_price,
                "change_percent": change_percent,
                "color": color
            }
            
            # Cache result
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"Error getting stock info for {symbol}: {e}")
            return None

    @retry_on_exception(max_retries=2, delay=0.5, exceptions=(Exception,))
    def get_stock_info_list(self, symbols: List[str]) -> Optional[Dict[str, Dict]]:
        """
        Lấy thông tin nhiều mã chứng khoán từ VCI
        
        Args:
            symbols: List mã chứng khoán
        
        Returns:
            Dict[symbol -> stock_info] hoặc None nếu lỗi
        """
        symbols = [s.upper() for s in symbols]
        
        # Check cache
        cache_key = f"list_{'_'.join(sorted(symbols))}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            stock = self.vnstock.stock(symbol="ABC", source="VCI")
            df = stock.trading.price_board(symbols_list=symbols)
            
            if df is None or df.empty:
                return None
            
            df.columns = ['_'.join(col) for col in df.columns]
            result = {}
            
            for _, row in df.iterrows():
                symbol = row["listing_symbol"]
                current_price = row.get("match_match_price")
                reference_price = row["listing_ref_price"]
                ceiling_price = row["listing_ceiling"]
                floor_price = row["listing_floor"]
                name_company = row["listing_organ_name"]
                
                # Tính phần trăm thay đổi và màu
                change_percent = 0
                if current_price and reference_price:
                    change_percent = ((current_price - reference_price) / reference_price) * 100
                
                color = self._calculate_stock_color(current_price, reference_price, ceiling_price, floor_price)

                result[symbol] = {
                    "symbol": symbol,
                    "name_company": name_company,
                    "ceiling_price": ceiling_price,
                    "floor_price": floor_price,
                    "reference_price": reference_price,
                    "current_price": current_price,
                    "change_percent": change_percent,
                    "color": color
                }
            
            # Cache result
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"Error getting stock info list: {e}")
            return None

    @retry_on_exception(max_retries=3, delay=1.0, exceptions=(requests.exceptions.RequestException,))
    def get_stock_info_list_v2(self, symbols: List[str]) -> Optional[Dict[str, Dict]]:
        """
        Lấy thông tin từ VietCap API trực tiếp (backup method)
        
        Args:
            symbols: List mã chứng khoán
        
        Returns:
            Dict[symbol -> stock_info] hoặc None nếu lỗi
        """
        symbols = [s.upper() for s in symbols]
        
        # Check cache
        cache_key = f"v2_{'_'.join(sorted(symbols))}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            payload = {"symbols": symbols}
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://trading.vietcap.com.vn",
                "Referer": "https://trading.vietcap.com.vn/"
            }
            
            response = self.session.post(
                self.vietcap_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            result = {}
            
            for item in data:
                symbol = item.get("s")
                current_price = item.get("c")
                reference_price = item.get("ref")
                ceiling_price = item.get("cei")
                floor_price = item.get("flo")
                name_company = item.get("orgn", "")
                
                # Tính phần trăm thay đổi và màu
                change_percent = 0
                if current_price and reference_price:
                    change_percent = ((current_price - reference_price) / reference_price) * 100
                
                color = self._calculate_stock_color(current_price, reference_price, ceiling_price, floor_price)

                result[symbol] = {
                    "symbol": symbol,
                    "name_company": name_company,
                    "ceiling_price": ceiling_price,
                    "floor_price": floor_price,
                    "reference_price": reference_price,
                    "current_price": current_price,
                    "change_percent": change_percent,
                    "color": color
                }
            
            # Cache result
            self._set_cache(cache_key, result)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling VietCap API: {e}")
            return None
        except Exception as e:
            print(f"Error parsing VietCap API response: {e}")
            return None
    
    def clear_cache(self):
        """Xóa toàn bộ cache"""
        self.cache.clear()
        self.last_cache_time.clear()


# Global instance
_stock_api = StockAPI()

# Backward compatibility - giữ nguyên interface cũ
def get_stock_info(symbol: str) -> Optional[Dict]:
    """Wrapper function for backward compatibility"""
    return _stock_api.get_stock_info(symbol)

def get_stock_info_list(symbols: List[str]) -> Optional[Dict[str, Dict]]:
    """Wrapper function for backward compatibility"""
    return _stock_api.get_stock_info_list(symbols)

def get_stock_info_list_v2(symbols: List[str]) -> Optional[Dict[str, Dict]]:
    """Wrapper function for backward compatibility"""
    return _stock_api.get_stock_info_list_v2(symbols)

def get_stock_info_list_smart(symbols: List[str]) -> Optional[Dict[str, Dict]]:
    """
    Smart function với fallback: Try v2 first, fallback to v1 if failed
    Ưu tiên v2 (VietCap API) vì nhanh hơn và ít timeout hơn
    
    Args:
        symbols: List mã chứng khoán
    
    Returns:
        Dict[symbol -> stock_info] hoặc None nếu cả 2 đều lỗi
    """
    # Try v2 first (VietCap API - faster)
    try:
        result = _stock_api.get_stock_info_list_v2(symbols)
        if result:
            return result
    except Exception as e:
        print(f"V2 API failed: {e}, trying v1...")
    
    # Fallback to v1 (vnstock)
    try:
        result = _stock_api.get_stock_info_list(symbols)
        if result:
            print(f"Fallback to v1 successful for {len(symbols)} symbols")
            return result
    except Exception as e:
        print(f"V1 API also failed: {e}")
    
    return None

# Example usage
if __name__ == "__main__":
    print("=== TEST STOCK API CLASS ===\n")
    
    # Test VietCap API v2 (nhanh nhất)
    print("1. Test VietCap API (v2)...")
    test_symbols = ["VCB", "FPT"]
    result_v2 = get_stock_info_list_v2(test_symbols)
    
    if result_v2:
        print("✅ VietCap API hoạt động:")
        for symbol, info in result_v2.items():
            print(f"  {symbol}: {info['current_price']:,.0f} VNĐ ({info['change_percent']:+.2f}%) - {info['color']}")
    else:
        print("❌ VietCap API lỗi")
    
    print("\n2. Test vnstock API...")
    result_v1 = get_stock_info_list(["VCB"])
    
    if result_v1:
        print("✅ Vnstock API hoạt động:")
        for symbol, info in result_v1.items():
            print(f"  {symbol}: {info['current_price']:,.0f} VNĐ ({info['change_percent']:+.2f}%)")
    else:
        print("❌ Vnstock API lỗi hoặc timeout")
    
    print("\n3. Test cache...")
    import time
    start = time.time()
    cached = get_stock_info_list_v2(test_symbols)  # Should be instant from cache
    elapsed = time.time() - start
    print(f"✅ Thời gian lấy từ cache: {elapsed:.3f}s (should be <0.01s)")
    
    print("\n=== DONE ===")
