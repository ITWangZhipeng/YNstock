# markdata/models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class StockQuote(BaseModel):
    """股票行情数据模型"""
    code: str  # 股票代码
    name: Optional[str] = None  # 股票名称
    open: float  # 开盘价
    close: float  # 收盘价
    high: float  # 最高价
    low: float  # 最低价
    volume: int  # 成交量
    amount: float  # 成交额
    pre_close: float  # 昨收价
    change: float  # 涨跌额
    pct_chg: float  # 涨跌幅(%)
    timestamp: datetime  # 时间戳

class SubscribeRequest(BaseModel):
    """订阅请求模型"""
    symbols: List[str]  # 订阅的股票代码列表
    frequency: str = "1m"  # 频率，默认1分钟

class MarketDataResponse(BaseModel):
    """市场数据响应模型"""
    type: str  # 数据类型: quote, kline, tick
    data: Dict[str, Any]  # 具体数据
    timestamp: datetime  # 接收时间

class ConnectionStatus(BaseModel):
    """连接状态模型"""
    status: str  # connected, disconnected, connecting
    message: Optional[str] = None
    timestamp: datetime