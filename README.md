# YNstock - 股票行情数据服务

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

YNstock 是一个功能强大的股票行情数据服务系统，提供多数据源集成、实时数据推送、历史数据查询和可视化分析功能。

## 主要特性

- **多数据源支持**: 集成 akshare、BaoStock、聚宽 JQData 等多个数据源
- **实时数据推送**: WebSocket 实时推送股票行情数据
- **历史数据查询**: 提供完整的股票历史数据 API
- **公司信息管理**: 上市公司基本信息、财务数据等
- **数据可视化**: 内置箱型图、趋势图等可视化工具
- **RESTful API**: 标准的 HTTP API 接口
- **可扩展架构**: 模块化设计，易于扩展新功能

## 快速开始

### 安装

1. 克隆项目
```bash
git clone <repository-url>
cd YNstock
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -e .
```

3. 配置环境变量
```bash
cp config/.env.example config/.env
# 编辑 config/.env 文件，设置聚宽账户等信息
```

4. 启动服务
```bash
python -m src.ynstock.main
```

服务启动后，访问 http://localhost:8000/docs 查看 API 文档。

### 基本使用

#### WebSocket 实时数据订阅

```python
import asyncio
import websockets
import json

async def subscribe_stock():
    async with websockets.connect('ws://localhost:8000/ws/market-data') as websocket:
        # 订阅股票
        subscribe_msg = {
            "type": "subscribe",
            "symbols": ["000001.XSHE", "600000.XSHG"],
            "frequency": "1m"
        }
        await websocket.send(json.dumps(subscribe_msg))

        # 接收实时数据
        while True:
            data = await websocket.recv()
            print(json.loads(data))

asyncio.run(subscribe_stock())
```

#### HTTP API 查询

```python
import requests

# 获取股票数据文件列表
response = requests.get('http://localhost:8000/api/stock-files')
print(response.json())

# 获取特定股票数据
response = requests.get('http://localhost:8000/api/stock-data/history_k_data')
print(response.json())
```

## 项目结构

```
YNstock/
├── src/                            # 源代码目录
│   ├── ynstock/                   # 主包
│   │   ├── api/                  # API层
│   │   │   ├── routers/          # HTTP路由
│   │   │   └── websocket/        # WebSocket处理
│   │   ├── core/                 # 核心模块
│   │   │   ├── config.py        # 配置管理
│   │   │   ├── models.py        # 数据模型
│   │   │   ├── exceptions.py    # 自定义异常
│   │   │   └── constants.py     # 常量定义
│   │   ├── services/            # 服务层
│   │   │   ├── market/          # 市场数据服务
│   │   │   ├── company/         # 公司信息服务
│   │   │   └── database/        # 数据库服务
│   │   ├── utils/               # 工具函数
│   │   │   ├── logger.py        # 日志配置
│   │   │   ├── validators.py    # 数据验证
│   │   │   ├── helpers.py       # 辅助函数
│   │   │   └── visualization.py # 可视化工具
│   │   └── main.py             # 应用入口
│   └── scripts/                # 脚本目录
│       ├── data_collection/    # 数据采集脚本
│       └── db/                 # 数据库脚本
├── tests/                      # 测试目录
├── data/                       # 数据目录
├── config/                     # 配置文件
├── docs/                       # 文档
└── pyproject.toml             # 项目配置
```

## 数据源支持

| 数据源 | 类型 | 功能 | 状态 |
|--------|------|------|------|
| akshare | 免费 | 实时行情、公司信息 | ✅ |
| BaoStock | 免费 | 历史K线数据 | ✅ |
| 聚宽 JQData | 付费 | 实时行情、历史数据 | ✅ |
| 东方财富 | 免费 | 公司基本信息 | ✅ |

## API 文档

详细的 API 文档请参考：
- 交互式文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- API 说明: [docs/api.md](docs/api.md)

## 配置说明

### 环境变量

重要环境变量：
```bash
# 聚宽账户（必需）
JQDATA_USERNAME=your_username
JQDATA_PASSWORD=your_password

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 日志级别
LOG_LEVEL=INFO
```

### 配置文件

- `config/settings.yaml`: 应用配置
- `config/logging.yaml`: 日志配置
- `config/.env.example`: 环境变量示例

## 开发指南

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
isort src/
flake8 src/
```

### 添加新数据源

1. 在 `src/ynstock/services/market/` 下创建新的数据源模块
2. 实现统一的数据接口
3. 在配置文件中启用数据源
4. 更新相关 API 和服务

## 部署

### 生产环境部署

详细部署指南请参考 [docs/deployment.md](docs/deployment.md)。

### Docker 部署

```bash
# 构建镜像
docker build -t ynstock .

# 运行容器
docker run -d -p 8000:8000 --name ynstock ynstock
```

### 系统服务部署

使用 systemd 管理服务：
```bash
sudo systemctl start ynstock
sudo systemctl enable ynstock
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/yourusername/YNstock)
- 问题反馈: [Issues](https://github.com/yourusername/YNstock/issues)
- 文档: [docs/](docs/)

## 致谢

感谢以下开源项目：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [akshare](https://github.com/akfamily/akshare) - 免费金融数据接口
- [BaoStock](http://baostock.com/) - 免费开源的证券数据平台
- [pandas](https://pandas.pydata.org/) - 数据分析工具
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包

---

**注意**: 本项目仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。