# markdata/jqdata_client.py
import asyncio
import json
import logging
from typing import List, Callable, Optional
from datetime import datetime
import jqdatasdk as jq
from ynstock.core.models import StockQuote, MarketDataResponse

logger = logging.getLogger(__name__)

class JQDataWebSocketClient:
    """基于jqdatasdk的行情数据客户端"""

    def __init__(self, username: str, password: str):
        """
        初始化JQData客户端

        Args:
            username: 聚宽用户名
            password: 聚宽密码
        """
        self.username = username
        self.password = password
        self.is_connected = False
        self.subscribed_symbols = set()
        self.data_callbacks = []
        self.running = False

    async def connect(self):
        """连接到JQData服务"""
        try:
            logger.info("正在连接JQData服务...")
            jq.auth(self.username, self.password)

            # 验证连接
            if jq.is_auth():
                self.is_connected = True
                logger.info("JQData连接成功")
                return True
            else:
                logger.error("JQData认证失败")
                return False

        except Exception as e:
            logger.error(f"JQData连接失败: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        self.is_connected = False
        self.running = False
        self.subscribed_symbols.clear()
        logger.info("JQData连接已断开")

    def subscribe(self, symbols: List[str]):
        """订阅股票行情"""
        if not self.is_connected:
            logger.warning("未连接到JQData服务")
            return False

        self.subscribed_symbols.update(symbols)
        logger.info(f"已订阅股票: {symbols}")
        return True

    def unsubscribe(self, symbols: List[str]):
        """取消订阅"""
        for symbol in symbols:
            self.subscribed_symbols.discard(symbol)
        logger.info(f"已取消订阅: {symbols}")

    async def start_listening(self, callback: Callable[[MarketDataResponse], None]):
        """开始监听行情数据"""
        if not self.is_connected:
            logger.error("请先连接到JQData服务")
            return

        self.data_callbacks.append(callback)
        self.running = True

        logger.info("开始监听行情数据...")

        while self.running and self.is_connected:
            try:
                # 获取实时行情数据
                if self.subscribed_symbols:
                    await self._fetch_realtime_data()

                # 控制请求频率，避免过于频繁
                await asyncio.sleep(1)  # 1秒间隔

            except Exception as e:
                logger.error(f"监听过程中出现错误: {e}")
                await asyncio.sleep(5)  # 出错后等待5秒重试

    async def _fetch_realtime_data(self):
        """获取实时行情数据"""
        try:
            # 使用jqdatasdk获取实时行情
            current_dt = datetime.now()

            for symbol in self.subscribed_symbols:
                try:
                    # 获取股票基本信息
                    security_info = jq.get_security_info(symbol)
                    if not security_info:
                        continue

                    # 获取最新行情数据
                    price_data = jq.get_price(
                        symbol,
                        end_date=current_dt.strftime('%Y-%m-%d'),
                        count=1,
                        frequency='1d'
                    )

                    if not price_data.empty:
                        latest_row = price_data.iloc[-1]

                        # 构造行情数据
                        quote = StockQuote(
                            code=symbol,
                            name=getattr(security_info, 'display_name', symbol),
                            open=float(latest_row['open']),
                            close=float(latest_row['close']),
                            high=float(latest_row['high']),
                            low=float(latest_row['low']),
                            volume=int(latest_row['volume']),
                            amount=float(latest_row['money']),
                            pre_close=float(latest_row['pre_close']) if 'pre_close' in latest_row else 0.0,
                            change=float(latest_row['close'] - latest_row['pre_close']) if 'pre_close' in latest_row else 0.0,
                            pct_chg=float((latest_row['close'] - latest_row['pre_close']) / latest_row['pre_close'] * 100) if 'pre_close' in latest_row and latest_row['pre_close'] != 0 else 0.0,
                            timestamp=current_dt
                        )

                        # 发送数据给回调函数
                        response = MarketDataResponse(
                            type="quote",
                            data=quote.dict(),
                            timestamp=current_dt
                        )

                        for callback in self.data_callbacks:
                            try:
                                callback(response)
                            except Exception as cb_error:
                                logger.error(f"回调函数执行错误: {cb_error}")

                except Exception as symbol_error:
                    logger.warning(f"获取{symbol}行情数据失败: {symbol_error}")
                    continue

        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")

    def add_callback(self, callback: Callable[[MarketDataResponse], None]):
        """添加数据回调函数"""
        self.data_callbacks.append(callback)

    def remove_callback(self, callback: Callable[[MarketDataResponse], None]):
        """移除数据回调函数"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)