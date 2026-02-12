"""
Formatting utilities for prices, messages, and display
"""


def format_price(price, currency: str = "VNĐ", show_currency: bool = False) -> str:
    """
    Format giá với dấu phẩy phân cách hàng nghìn
    
    Args:
        price: Giá cần format
        currency: Đơn vị tiền tệ (mặc định VNĐ)
        show_currency: Có hiển thị đơn vị tiền tệ không
    
    Returns:
        Chuỗi giá đã format
    
    Examples:
        >>> format_price(1234567)
        '1,234,567'
        >>> format_price(1234567, show_currency=True)
        '1,234,567 VNĐ'
        >>> format_price(None)
        'N/A'
    """
    if price is None:
        return "N/A"
    
    formatted = f"{price:,.0f}"
    
    if show_currency:
        formatted += f" {currency}"
    
    return formatted


def format_percentage(value: float, decimals: int = 2, show_sign: bool = True) -> str:
    """
    Format phần trăm với dấu + hoặc -
    
    Args:
        value: Giá trị phần trăm
        decimals: Số chữ số thập phân
        show_sign: Hiển thị dấu + cho số dương
    
    Returns:
        Chuỗi phần trăm đã format
    
    Examples:
        >>> format_percentage(5.5)
        '+5.50%'
        >>> format_percentage(-3.2)
        '-3.20%'
        >>> format_percentage(0)
        '0.00%'
    """
    if value is None:
        return "N/A"
    
    sign = ""
    if show_sign and value > 0:
        sign = "+"
    elif value < 0:
        sign = "-"
        value = abs(value)
    
    return f"{sign}{value:.{decimals}f}%"


def get_stock_color_indicator(color: str) -> str:
    """
    Lấy emoji chấm màu theo trạng thái chứng khoán
    
    Args:
        color: Màu trạng thái (green, red, purple, cyan, yellow)
    
    Returns:
        Emoji tương ứng
    """
    color_map = {
        "green": "🟢",   # Tăng giá
        "red": "🔴",     # Giảm giá
        "purple": "🟣",  # Giá trần
        "cyan": "🔵",    # Giá sàn
        "yellow": "🟡"   # Giá tham chiếu
    }
    return color_map.get(color.lower(), "⚪")


def format_number_short(number: int) -> str:
    """
    Format số lớn thành dạng ngắn gọn (K, M, B)
    
    Args:
        number: Số cần format
    
    Returns:
        Chuỗi số đã format
    
    Examples:
        >>> format_number_short(1500)
        '1.5K'
        >>> format_number_short(2500000)
        '2.5M'
        >>> format_number_short(1000000000)
        '1B'
    """
    if number is None:
        return "N/A"
    
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Cắt ngắn text nếu quá dài
    
    Args:
        text: Text cần cắt
        max_length: Độ dài tối đa
        suffix: Hậu tố khi cắt
    
    Returns:
        Text đã cắt hoặc nguyên bản nếu ngắn hơn max_length
    """
    if text is None:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
