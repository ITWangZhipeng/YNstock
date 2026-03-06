"""数据验证工具"""
import re
from typing import Optional, Union, List

def validate_stock_code(code: str) -> bool:
    """
    验证股票代码格式

    Args:
        code: 股票代码

    Returns:
        是否有效
    """
    # 标准A股代码：6位数字
    if not isinstance(code, str):
        return False

    # 移除可能的前缀（如 sh., sz., bj.）
    clean_code = code.lower().replace('sh.', '').replace('sz.', '').replace('bj.', '')

    # 检查是否为6位数字
    if not re.match(r'^\d{6}$', clean_code):
        return False

    # 检查市场前缀（可选）
    first_digit = clean_code[0]
    if first_digit == '6':
        # 沪市
        return True
    elif first_digit in ['0', '3']:
        # 深市
        return True
    elif first_digit == '8':
        # 北交所
        return True
    else:
        # 未知市场
        return False

def validate_date_format(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
    """
    验证日期字符串格式

    Args:
        date_str: 日期字符串
        fmt: 期望的格式

    Returns:
        是否有效
    """
    try:
        from datetime import datetime
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False

def validate_frequency(frequency: str) -> bool:
    """
    验证数据频率

    Args:
        frequency: 频率字符串

    Returns:
        是否有效
    """
    valid_frequencies = ['1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M']
    return frequency in valid_frequencies

def validate_price(price: Union[int, float]) -> bool:
    """
    验证价格是否合理

    Args:
        price: 价格

    Returns:
        是否有效
    """
    if not isinstance(price, (int, float)):
        return False
    return price >= 0

def validate_volume(volume: Union[int, float]) -> bool:
    """
    验证成交量是否合理

    Args:
        volume: 成交量

    Returns:
        是否有效
    """
    if not isinstance(volume, (int, float)):
        return False
    return volume >= 0

def validate_symbols(symbols: List[str]) -> List[str]:
    """
    验证并清理股票代码列表

    Args:
        symbols: 股票代码列表

    Returns:
        有效的股票代码列表
    """
    valid_symbols = []
    for symbol in symbols:
        if validate_stock_code(symbol):
            valid_symbols.append(symbol)
    return valid_symbols