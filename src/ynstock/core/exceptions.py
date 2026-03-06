"""自定义异常类"""

class YNStockError(Exception):
    """基础异常类"""
    pass

class ConfigError(YNStockError):
    """配置错误"""
    pass

class DataSourceError(YNStockError):
    """数据源错误"""
    pass

class ValidationError(YNStockError):
    """数据验证错误"""
    pass

class DatabaseError(YNStockError):
    """数据库错误"""
    pass

class WebSocketError(YNStockError):
    """WebSocket错误"""
    pass