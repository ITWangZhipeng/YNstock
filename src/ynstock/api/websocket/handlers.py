# markdata/websocket_handler.py
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from ynstock.core.models import SubscribeRequest, MarketDataResponse
from ynstock.api.websocket.clients.jqdata import JQDataWebSocketClient

logger = logging.getLogger(__name__)

class MarketDataWebSocketManager:
    """行情数据WebSocket管理器"""

    def __init__(self, jq_username: str, jq_password: str):
        self.jq_client = JQDataWebSocketClient(jq_username, jq_password)
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscribed_symbols: Set[str] = set()
        self.client_id_counter = 0

    async def connect(self, websocket: WebSocket):
        """处理新的WebSocket连接"""
        await websocket.accept()
        client_id = f"client_{self.client_id_counter}"
        self.client_id_counter += 1
        self.active_connections[client_id] = websocket

        logger.info(f"新客户端连接: {client_id}")

        # 发送连接成功的消息
        await self.send_personal_message({
            "type": "connection_status",
            "status": "connected",
            "client_id": client_id,
            "message": "行情数据WebSocket连接成功"
        }, client_id)

        return client_id

    def disconnect(self, client_id: str):
        """处理客户端断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"客户端断开连接: {client_id}")

    async def send_personal_message(self, message: dict, client_id: str):
        """向特定客户端发送消息"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"向客户端{client_id}发送消息失败: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict):
        """向所有连接的客户端广播消息"""
        if not self.active_connections:
            return

        disconnected_clients = []
        message_str = json.dumps(message, ensure_ascii=False)

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"向客户端{client_id}广播消息失败: {e}")
                disconnected_clients.append(client_id)

        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def handle_subscription(self, client_id: str, subscribe_request: SubscribeRequest):
        """处理订阅请求"""
        try:
            # 更新订阅列表
            new_symbols = set(subscribe_request.symbols)
            symbols_to_add = new_symbols - self.subscribed_symbols
            symbols_to_remove = self.subscribed_symbols - new_symbols

            # 处理新增订阅
            if symbols_to_add:
                if not self.jq_client.is_connected:
                    success = await self.jq_client.connect()
                    if not success:
                        await self.send_personal_message({
                            "type": "error",
                            "message": "无法连接到行情服务"
                        }, client_id)
                        return

                self.jq_client.subscribe(list(symbols_to_add))
                self.subscribed_symbols.update(symbols_to_add)
                logger.info(f"新增订阅: {symbols_to_add}")

            # 处理取消订阅
            if symbols_to_remove:
                self.jq_client.unsubscribe(list(symbols_to_remove))
                self.subscribed_symbols.difference_update(symbols_to_remove)
                logger.info(f"取消订阅: {symbols_to_remove}")

            # 发送订阅确认
            await self.send_personal_message({
                "type": "subscription_confirm",
                "subscribed_symbols": list(self.subscribed_symbols),
                "message": f"订阅更新成功，当前订阅数量: {len(self.subscribed_symbols)}"
            }, client_id)

        except Exception as e:
            logger.error(f"处理订阅请求失败: {e}")
            await self.send_personal_message({
                "type": "error",
                "message": f"订阅处理失败: {str(e)}"
            }, client_id)

    async def start_market_data_service(self):
        """启动行情数据服务"""
        if not self.jq_client.is_connected:
            logger.warning("行情服务未连接，等待客户端订阅后再启动")
            return

        # 添加数据回调
        def data_callback(response: MarketDataResponse):
            # 在事件循环中执行异步操作
            asyncio.create_task(self.broadcast(response.dict()))

        self.jq_client.add_callback(data_callback)

        # 启动监听
        await self.jq_client.start_listening(data_callback)

    async def stop_market_data_service(self):
        """停止行情数据服务"""
        self.jq_client.disconnect()
        self.subscribed_symbols.clear()

# 全局WebSocket管理器实例
websocket_manager: Optional[MarketDataWebSocketManager] = None

async def get_websocket_manager(jq_username: str, jq_password: str) -> MarketDataWebSocketManager:
    """获取WebSocket管理器实例"""
    global websocket_manager
    if websocket_manager is None:
        websocket_manager = MarketDataWebSocketManager(jq_username, jq_password)
    return websocket_manager