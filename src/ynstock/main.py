# 修改后的 main.py
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
from typing import Optional
import logging
from dotenv import load_dotenv
import json
from datetime import datetime

# 导入行情数据模块
from .api.websocket.handlers import get_websocket_manager, SubscribeRequest
from .core.models import MarketDataResponse

# 加载环境变量
load_dotenv()

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

app = FastAPI(title="股票行情数据服务", version="1.0.0")

# 从环境变量读取聚宽账户配置
JQ_USERNAME = os.getenv("JQDATA_USERNAME", "")
JQ_PASSWORD = os.getenv("JQDATA_PASSWORD", "")

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# WebSocket配置
WEBSOCKET_HEARTBEAT_INTERVAL = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30"))
WEBSOCKET_MAX_CONNECTIONS = int(os.getenv("WEBSOCKET_MAX_CONNECTIONS", "100"))
WEBSOCKET_TIMEOUT = int(os.getenv("WEBSOCKET_TIMEOUT", "60"))

# 数据获取配置
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "1"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))

@app.get("/get/k")
async def root():
    return {"message": "Hello World"}

@app.get("/api/stock-data/{filename}")
async def get_stock_data(filename: str):
    """
    获取股票CSV数据

    Args:
        filename (str): 文件名，例如: history_k_data

    Returns:
        dict: 包含CSV数据的JSON响应
    """
    try:
        # 构建文件路径
        file_path = f"../../data/raw/market/{filename}.csv"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"文件 {filename}.csv 不存在")

        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 转换为字典格式返回
        data = df.to_dict(orient='records')

        return {
            "filename": filename,
            "total_records": len(data),
            "columns": list(df.columns),
            "data": data
        }

    except HTTPException:
        # 重新抛出已有的HTTP异常
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="文件未找到")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/api/stock-files")
async def list_stock_files():
    """
    列出所有可用的股票数据文件

    Returns:
        dict: 文件列表
    """
    try:
        stock_dir = "../../data/raw/market"
        if not os.path.exists(stock_dir):
            return {"files": []}

        # 查找所有CSV文件
        csv_files = [f[:-4] for f in os.listdir(stock_dir) if f.endswith('.csv')]

        return {
            "files": csv_files,
            "count": len(csv_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@app.websocket("/ws/market-data")
async def websocket_market_data(websocket: WebSocket):
    """行情数据WebSocket端点"""
    try:
        # 获取WebSocket管理器
        manager = await get_websocket_manager(JQ_USERNAME, JQ_PASSWORD)

        # 建立连接
        client_id = await manager.connect(websocket)

        try:
            while True:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)

                # 处理不同类型的请求
                if message.get("type") == "subscribe":
                    subscribe_request = SubscribeRequest(**message)
                    await manager.handle_subscription(client_id, subscribe_request)

                elif message.get("type") == "unsubscribe":
                    symbols = message.get("symbols", [])
                    manager.jq_client.unsubscribe(symbols)
                    # 更新全局订阅列表
                    manager.subscribed_symbols.difference_update(symbols)
                    await manager.send_personal_message({
                        "type": "unsubscription_confirm",
                        "message": f"已取消订阅: {symbols}"
                    }, client_id)

                elif message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, client_id)

        except WebSocketDisconnect:
            logger.info(f"客户端 {client_id} 断开连接")
        except Exception as e:
            logger.error(f"处理WebSocket消息时出错: {e}")
        finally:
            manager.disconnect(client_id)

    except Exception as e:
        logger.error(f"WebSocket连接处理失败: {e}")
        await websocket.close()

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == '__main__':
    import uvicorn
    import sys
    import json
    from datetime import datetime

    # 解析命令行参数
    port = 8000
    if '--port' in sys.argv:
        try:
            port_index = sys.argv.index('--port') + 1
            if port_index < len(sys.argv):
                port = int(sys.argv[port_index])
        except (ValueError, IndexError):
            print("端口参数无效，使用默认端口8000")

    # 验证聚宽账户配置
    if not JQ_USERNAME or not JQ_PASSWORD:
        print("警告: 未配置聚宽账户信息，请在.env文件中设置JQDATA_USERNAME和JQDATA_PASSWORD")

    print(f"启动服务器，主机: {SERVER_HOST}，端口: {SERVER_PORT}")
    print(f"行情数据WebSocket端点: ws://{SERVER_HOST}:{SERVER_PORT}/ws/market-data")
    print(f"HTTP API端点: http://{SERVER_HOST}:{SERVER_PORT}/docs")

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)