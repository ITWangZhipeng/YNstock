import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置测试环境变量
os.environ["JQDATA_USERNAME"] = "test_user"
os.environ["JQDATA_PASSWORD"] = "test_pass"
os.environ["LOG_LEVEL"] = "ERROR"
os.environ["SERVER_HOST"] = "127.0.0.1"
os.environ["SERVER_PORT"] = "0"  # 使用随机端口
os.environ["WEBSOCKET_HEARTBEAT_INTERVAL"] = "5"
os.environ["WEBSOCKET_MAX_CONNECTIONS"] = "10"
os.environ["WEBSOCKET_TIMEOUT"] = "5"
os.environ["FETCH_INTERVAL"] = "1"
os.environ["MAX_RETRY_ATTEMPTS"] = "1"
os.environ["RETRY_DELAY"] = "1"

# 导入主应用之前，先模拟websocket管理器
# 创建模拟管理器类
class MockMarketDataWebSocketManager:
    def __init__(self, jq_username, jq_password):
        self.jq_client = Mock()
        self.jq_client.is_connected = False
        self.jq_client.connect = AsyncMock(return_value=True)
        self.jq_client.disconnect = Mock()
        self.jq_client.subscribe = Mock()
        self.jq_client.unsubscribe = Mock()
        self.jq_client.add_callback = Mock()
        self.jq_client.start_listening = AsyncMock()
        self.active_connections = {}
        self.subscribed_symbols = set()
        self.client_id_counter = 0

    async def connect(self, websocket):
        await websocket.accept()
        client_id = f"client_{self.client_id_counter}"
        self.client_id_counter += 1
        self.active_connections[client_id] = websocket
        return client_id

    def disconnect(self, client_id):
        self.active_connections.pop(client_id, None)

    async def send_personal_message(self, message, client_id):
        pass

    async def broadcast(self, message):
        pass

    async def handle_subscription(self, client_id, subscribe_request):
        pass

    async def start_market_data_service(self):
        pass

    async def stop_market_data_service(self):
        pass


# 模拟get_websocket_manager函数
async def mock_get_websocket_manager(jq_username, jq_password):
    return MockMarketDataWebSocketManager(jq_username, jq_password)


# 应用补丁
patcher = patch('work.marketdata.websocket_handler.get_websocket_manager', mock_get_websocket_manager)
patcher.start()

# 现在导入主应用（补丁已经应用）
from main import app

# 在测试结束后停止补丁
@pytest.fixture(scope="session", autouse=True)
def stop_patch():
    yield
    patcher.stop()


@pytest.fixture
def client():
    """提供测试客户端"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_websocket_manager():
    """提供模拟的websocket管理器"""
    # 由于已经全局模拟，可以直接获取实例
    # 但我们需要获取模拟的实例，这里简单返回一个模拟对象
    return MockMarketDataWebSocketManager("test", "test")