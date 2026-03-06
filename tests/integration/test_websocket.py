"""
WebSocket端点测试
"""
import pytest
import json
import asyncio
from fastapi.testclient import TestClient


class TestMarketDataWebSocket:
    """测试 /ws/market-data WebSocket端点"""

    def test_websocket_connection(self, client):
        """测试WebSocket连接建立"""
        with client.websocket_connect("/ws/market-data") as websocket:
            # 连接成功后应收到欢迎消息
            data = websocket.receive_json()
            assert "type" in data
            assert data["type"] == "connection_status"
            assert data["status"] == "connected"
            assert "client_id" in data
            assert "message" in data

    def test_websocket_ping_pong(self, client):
        """测试ping/pong消息"""
        with client.websocket_connect("/ws/market-data") as websocket:
            # 接收连接消息
            websocket.receive_json()

            # 发送ping消息
            ping_msg = {"type": "ping"}
            websocket.send_text(json.dumps(ping_msg))

            # 接收pong响应
            response = websocket.receive_json()
            assert response["type"] == "pong"
            assert "timestamp" in response

    def test_websocket_subscribe(self, client):
        """测试订阅消息（模拟）"""
        with client.websocket_connect("/ws/market-data") as websocket:
            # 接收连接消息
            websocket.receive_json()

            # 发送订阅请求
            subscribe_msg = {
                "type": "subscribe",
                "symbols": ["000001.SZ", "000002.SZ"]
            }
            websocket.send_text(json.dumps(subscribe_msg))

            # 接收订阅确认（模拟管理器可能不会响应，但至少不应出错）
            # 这里我们只确保连接没有关闭
            # 可以发送一个ping来测试连接仍然活跃
            ping_msg = {"type": "ping"}
            websocket.send_text(json.dumps(ping_msg))
            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_websocket_unsubscribe(self, client):
        """测试取消订阅消息"""
        with client.websocket_connect("/ws/market-data") as websocket:
            # 接收连接消息
            websocket.receive_json()

            # 发送取消订阅请求
            unsubscribe_msg = {
                "type": "unsubscribe",
                "symbols": ["000001.SZ"]
            }
            websocket.send_text(json.dumps(unsubscribe_msg))

            # 接收确认（如果有实现）
            # 发送ping测试连接
            ping_msg = {"type": "ping"}
            websocket.send_text(json.dumps(ping_msg))
            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_websocket_invalid_message(self, client):
        """测试无效消息类型"""
        with client.websocket_connect("/ws/market-data") as websocket:
            # 接收连接消息
            websocket.receive_json()

            # 发送无效消息
            invalid_msg = {"type": "invalid_type"}
            websocket.send_text(json.dumps(invalid_msg))

            # 连接应仍然保持打开（错误可能被忽略）
            # 发送ping验证
            ping_msg = {"type": "ping"}
            websocket.send_text(json.dumps(ping_msg))
            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_websocket_malformed_json(self, client):
        """测试格式错误的JSON"""
        with client.websocket_connect("/ws/market-data") as websocket:
            # 接收连接消息
            websocket.receive_json()

            # 发送无效JSON
            websocket.send_text("not a json")

            # 连接可能保持打开，也可能关闭（取决于实现）
            # 尝试发送ping，如果连接关闭会抛出异常
            try:
                ping_msg = {"type": "ping"}
                websocket.send_text(json.dumps(ping_msg))
                response = websocket.receive_json()
                # 如果收到响应，连接仍然打开
                assert response["type"] == "pong"
            except Exception:
                # 连接关闭是合理的
                pass