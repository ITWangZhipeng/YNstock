# YNstock API 文档

## 概述

YNstock 提供股票行情数据的 HTTP API 和 WebSocket 接口。

## 基础信息

- 基础 URL: `http://localhost:8000`
- WebSocket URL: `ws://localhost:8000/ws/market-data`
- API 文档: `http://localhost:8000/docs` (Swagger UI)
- 备用文档: `http://localhost:8000/redoc` (ReDoc)

## HTTP API 端点

### 健康检查

```http
GET /get/k
```

响应：
```json
{
  "message": "Hello World"
}
```

### 问候接口

```http
GET /hello/{name}
```

参数：
- `name` (路径参数): 用户名

响应：
```json
{
  "message": "Hello {name}"
}
```

### 获取股票数据文件列表

```http
GET /api/stock-files
```

响应：
```json
{
  "files": ["history_k_data", "other_data"],
  "count": 2
}
```

### 获取特定股票数据文件

```http
GET /api/stock-data/{filename}
```

参数：
- `filename` (路径参数): 文件名（不带 .csv 后缀）

响应：
```json
{
  "filename": "history_k_data",
  "total_records": 1000,
  "columns": ["date", "code", "open", "high", "low", "close", "volume", "amount"],
  "data": [...]
}
```

## WebSocket API

### 连接

连接到 WebSocket 端点：
```
ws://localhost:8000/ws/market-data
```

连接成功后，服务器会发送连接确认消息：
```json
{
  "type": "connection_status",
  "status": "connected",
  "client_id": "client_0",
  "message": "行情数据WebSocket连接成功"
}
```

### 消息类型

#### 1. Ping/Pong 心跳

客户端发送 Ping 消息：
```json
{
  "type": "ping"
}
```

服务器响应 Pong 消息：
```json
{
  "type": "pong",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### 2. 订阅行情数据

客户端发送订阅请求：
```json
{
  "type": "subscribe",
  "symbols": ["000001.XSHE", "600000.XSHG"],
  "frequency": "1m"
}
```

参数：
- `symbols`: 股票代码列表（支持带市场后缀）
- `frequency`: 数据频率，可选值: "1m", "5m", "15m", "30m", "60m", "1d"

服务器响应订阅确认：
```json
{
  "type": "subscription_confirm",
  "subscribed_symbols": ["000001.XSHE", "600000.XSHG"],
  "message": "订阅更新成功，当前订阅数量: 2"
}
```

#### 3. 取消订阅

客户端发送取消订阅请求：
```json
{
  "type": "unsubscribe",
  "symbols": ["000001.XSHE"]
}
```

服务器响应取消订阅确认：
```json
{
  "type": "unsubscription_confirm",
  "message": "已取消订阅: ['000001.XSHE']"
}
```

#### 4. 实时行情数据推送

服务器推送行情数据：
```json
{
  "type": "quote",
  "data": {
    "code": "000001.XSHE",
    "name": "平安银行",
    "open": 10.5,
    "close": 10.8,
    "high": 11.0,
    "low": 10.4,
    "volume": 1000000,
    "amount": 10800000.0,
    "pre_close": 10.3,
    "change": 0.5,
    "pct_chg": 4.85,
    "timestamp": "2024-01-01T12:00:00.000000"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 错误处理

错误消息格式：
```json
{
  "type": "error",
  "message": "错误描述"
}
```

## 数据格式说明

### 股票代码格式

- 标准格式: `000001.XSHE` (深圳), `600000.XSHG` (上海)
- 简写格式: `000001`, `600000` (自动识别市场)

### 时间格式

所有时间字段使用 ISO 8601 格式：
```
YYYY-MM-DDTHH:MM:SS.ssssss
```

## 使用示例

### Python 客户端示例

```python
import asyncio
import websockets
import json

async def subscribe_stock_data():
    uri = "ws://localhost:8000/ws/market-data"

    async with websockets.connect(uri) as websocket:
        # 接收连接确认
        response = await websocket.recv()
        print(f"连接成功: {response}")

        # 订阅股票
        subscribe_msg = {
            "type": "subscribe",
            "symbols": ["000001.XSHE", "600000.XSHG"],
            "frequency": "1m"
        }
        await websocket.send(json.dumps(subscribe_msg))

        # 接收订阅确认
        response = await websocket.recv()
        print(f"订阅确认: {response}")

        # 接收实时数据
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            if data["type"] == "quote":
                print(f"收到行情数据: {data}")

asyncio.run(subscribe_stock_data())
```

### JavaScript 客户端示例

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market-data');

ws.onopen = () => {
    console.log('WebSocket连接已建立');

    // 订阅股票
    const subscribeMsg = {
        type: 'subscribe',
        symbols: ['000001.XSHE', '600000.XSHG'],
        frequency: '1m'
    };
    ws.send(JSON.stringify(subscribeMsg));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);

    if (data.type === 'quote') {
        console.log('行情数据:', data.data);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
};

ws.onclose = () => {
    console.log('WebSocket连接已关闭');
};
```