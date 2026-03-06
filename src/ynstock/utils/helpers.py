"""辅助函数"""
import os
import time
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

def get_project_root() -> str:
    """
    获取项目根目录路径

    Returns:
        项目根目录路径
    """
    # 假设此文件在 src/ynstock/utils/helpers.py
    # 项目根目录是 src 的父目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

def ensure_directory_exists(directory: str) -> bool:
    """
    确保目录存在，如果不存在则创建

    Args:
        directory: 目录路径

    Returns:
        是否成功
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败 {directory}: {e}")
        return False

def format_timestamp(timestamp: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化时间戳

    Args:
        timestamp: 时间戳，默认为当前时间
        fmt: 格式字符串

    Returns:
        格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(fmt)

def parse_timestamp(timestamp_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析时间字符串

    Args:
        timestamp_str: 时间字符串
        fmt: 格式字符串

    Returns:
        时间戳对象，解析失败返回 None
    """
    try:
        return datetime.strptime(timestamp_str, fmt)
    except ValueError:
        return None

def calculate_md5(data: str) -> str:
    """
    计算字符串的MD5哈希值

    Args:
        data: 输入字符串

    Returns:
        MD5哈希值
    """
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
        exceptions: 要捕获的异常类型
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        raise last_exception
            raise last_exception
        return wrapper
    return decorator

def safe_get(data: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """
    安全获取嵌套字典中的值

    Args:
        data: 字典数据
        keys: 键路径，用 '.' 分隔
        default: 默认值

    Returns:
        找到的值或默认值
    """
    current = data
    for key in keys.split('.'):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def human_readable_size(size_bytes: int) -> str:
    """
    将字节大小转换为人类可读的格式

    Args:
        size_bytes: 字节大小

    Returns:
        人类可读的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"