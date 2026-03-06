"""常量定义"""

# 市场类型
MARKET_SH = "SH"  # 上海
MARKET_SZ = "SZ"  # 深圳
MARKET_BJ = "BJ"  # 北京

# 数据频率
FREQUENCY_1M = "1m"
FREQUENCY_5M = "5m"
FREQUENCY_15M = "15m"
FREQUENCY_30M = "30m"
FREQUENCY_60M = "60m"
FREQUENCY_1D = "1d"
FREQUENCY_1W = "1w"
FREQUENCY_1M = "1M"

# WebSocket消息类型
WS_TYPE_CONNECTION_STATUS = "connection_status"
WS_TYPE_SUBSCRIPTION_CONFIRM = "subscription_confirm"
WS_TYPE_UNSUBSCRIPTION_CONFIRM = "unsubscription_confirm"
WS_TYPE_QUOTE = "quote"
WS_TYPE_KLINE = "kline"
WS_TYPE_TICK = "tick"
WS_TYPE_PING = "ping"
WS_TYPE_PONG = "pong"
WS_TYPE_ERROR = "error"

# API路径
API_PREFIX = "/api"
WS_PREFIX = "/ws"

# 数据库表名
TABLE_STOCK_BASIC = "stock_basic"
TABLE_STOCK_REALTIME = "stock_realtime"
TABLE_MARKET_DATA = "market_data"

# 默认值
DEFAULT_PAGE_SIZE = 20
DEFAULT_MAX_CONNECTIONS = 100
DEFAULT_HEARTBEAT_INTERVAL = 30