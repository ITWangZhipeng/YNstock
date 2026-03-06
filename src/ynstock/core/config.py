# markdata/config.py
import os
from typing import Optional

class Config:
    """行情数据配置类"""

    # 聚宽账户配置
    JQDATA_USERNAME: str = os.getenv("JQDATA_USERNAME", "")
    JQDATA_PASSWORD: str = os.getenv("JQDATA_PASSWORD", "")

    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30  # 心跳间隔（秒）
    WEBSOCKET_MAX_CONNECTIONS: int = 100     # 最大连接数
    WEBSOCKET_TIMEOUT: int = 60              # 连接超时时间（秒）

    # 数据获取配置
    FETCH_INTERVAL: int = 1                  # 数据获取间隔（秒）
    MAX_RETRY_ATTEMPTS: int = 3              # 最大重试次数
    RETRY_DELAY: int = 5                     # 重试延迟（秒）

    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否完整"""
        if not cls.JQDATA_USERNAME or not cls.JQDATA_PASSWORD:
            print("警告: 未设置聚宽账户信息，请设置环境变量 JQDATA_USERNAME 和 JQDATA_PASSWORD")
            return False
        return True

# 创建配置实例
config = Config()