import pytest
import asyncio
import json
import websockets
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from work.marketdata.websocket_handler import MarketDataWebSocketManager
from work.marketdata.models import SubscribeRequest

@pytest.fixture
def client():
    """创建FastAPI测试客户端"""
    return TestClient(app)

@pytest.fixture
def websocket_url():
    """WebSocket测试URL"""
    return "ws://127.0.0.1:8000/ws/market-data"

class TestWebSocketMarketData:
    """WebSocket行情数据接口测试类"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, websocket_url):
        """测试WebSocket基本连接"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # 等待连接确认消息
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                assert data["type"] == "connection_status"
                assert data["status"] == "connected"
                assert "client_id" in data
                assert "message" in data

                print(f"✓ 连接成功，客户端ID: {data['client_id']}")

        except Exception as e:
            pytest.fail(f"WebSocket连接失败: {e}")

    @pytest.mark.asyncio
    async def test_ping_pong(self, websocket_url):
        """测试ping/pong心跳机制"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # 先接收连接确认
                await websocket.recv()

                # 发送ping消息
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))

                # 等待pong响应
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                assert data["type"] == "pong"
                assert "timestamp" in data

                print("✓ Ping/Pong测试通过")

        except Exception as e:
            pytest.fail(f"Ping/Pong测试失败: {e}")

    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe(self, websocket_url):
        """测试订阅和取消订阅功能"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # 先接收连接确认
                connection_msg = await websocket.recv()
                client_id = json.loads(connection_msg)["client_id"]

                # 测试订阅
                subscribe_msg = {
                    "type": "subscribe",
                    "symbols": ["000001.XSHE", "600000.XSHG"],
                    "frequency": "1m"
                }
                await websocket.send(json.dumps(subscribe_msg))

                # 等待订阅确认
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(response)

                assert data["type"] == "subscription_confirm"
                assert "subscribed_symbols" in data
                assert len(data["subscribed_symbols"]) >= 0

                print(f"✓ 订阅测试通过，当前订阅: {data['subscribed_symbols']}")

                # 测试取消订阅
                unsubscribe_msg = {
                    "type": "unsubscribe",
                    "symbols": ["000001.XSHE"]
                }
                await websocket.send(json.dumps(unsubscribe_msg))

                # 等待取消订阅确认
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                assert data["type"] == "unsubscription_confirm"
                assert "已取消订阅" in data["message"]

                print("✓ 取消订阅测试通过")

        except Exception as e:
            pytest.fail(f"订阅/取消订阅测试失败: {e}")

    @pytest.mark.asyncio
    async def test_multiple_clients(self, websocket_url):
        """测试多客户端连接"""
        clients = []
        try:
            # 创建多个客户端连接
            for i in range(3):
                websocket = await websockets.connect(websocket_url)
                clients.append(websocket)

                # 接收各自的连接确认
                response = await websocket.recv()
                data = json.loads(response)
                assert data["type"] == "connection_status"
                print(f"✓ 客户端{i+1}连接成功: {data['client_id']}")

            # 关闭所有连接
            for client in clients:
                await client.close()

            print("✓ 多客户端测试通过")

        except Exception as e:
            pytest.fail(f"多客户端测试失败: {e}")
        finally:
            # 确保清理所有连接
            for client in clients:
                if not client.closed:
                    await client.close()

    @pytest.mark.asyncio
    async def test_invalid_message_format(self, websocket_url):
        """测试无效消息格式处理"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # 先接收连接确认
                await websocket.recv()

                # 发送无效格式的消息
                invalid_msg = {"invalid": "message"}
                await websocket.send(json.dumps(invalid_msg))

                # 发送后应该不会收到错误响应（因为没有type字段）
                # 但连接应该保持正常

                # 再发送一个有效的ping来验证连接仍然正常
                ping_msg = {"type": "ping"}
                await websocket.send(json.dumps(ping_msg))

                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                assert data["type"] == "pong"
                print("✓ 无效消息格式处理测试通过")

        except Exception as e:
            pytest.fail(f"无效消息格式测试失败: {e}")

    def test_http_endpoints_work(self, client):
        """测试相关的HTTP端点是否正常工作"""
        # 测试根路径
        response = client.get("/get/k")
        assert response.status_code == 200
        assert response.json()["message"] == "Hello World"

        # 测试股票文件列表
        response = client.get("/api/stock-files")
        assert response.status_code == 200
        assert "files" in response.json()

        print("✓ HTTP端点测试通过")

# 单独运行测试的辅助函数
async def run_single_test():
    """运行单个测试用例"""
    url = "ws://127.0.0.1:8000/ws/market-data"

    print("开始测试WebSocket连接...")
    async with websockets.connect(url) as websocket:
        # 接收连接确认
        response = await websocket.recv()
        data = json.loads(response)
        print(f"连接成功: {data}")

        # 测试ping
        await websocket.send(json.dumps({"type": "ping"}))
        pong_response = await websocket.recv()
        print(f"Pong响应: {json.loads(pong_response)}")

        # 测试订阅
        subscribe_msg = {
            "type": "subscribe",
            "symbols": ["000001.XSHE"],
            "frequency": "1m"
        }
        await websocket.send(json.dumps(subscribe_msg))
        sub_response = await websocket.recv()
        print(f"订阅响应: {json.loads(sub_response)}")

        print("测试完成!")

if __name__ == "__main__":
    # 如果直接运行此文件，执行简单的连接测试
    print("运行简单WebSocket测试...")
    asyncio.run(run_single_test())
