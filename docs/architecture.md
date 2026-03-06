# YNstock 系统架构

## 概述

YNstock 是一个股票行情数据服务系统，提供多数据源集成、实时数据推送、历史数据查询等功能。系统采用分层架构设计，具有良好的可扩展性和可维护性。

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      客户端 (Web/App)                        │
└─────────────────┬───────────────────┬───────────────────────┘
                  │                   │
          HTTP API (REST)      WebSocket (实时推送)
                  │                   │
    ┌─────────────▼───────────────────▼─────────────┐
    │             FastAPI 应用服务器                 │
    │  ┌─────────────────────────────────────────┐  │
    │  │             API 层                      │  │
    │  │  • HTTP 路由 (REST API)                 │  │
    │  │  • WebSocket 处理器                     │  │
    │  │  • 请求验证和序列化                     │  │
    │  └─────────────────────────────────────────┘  │
    │  ┌─────────────────────────────────────────┐  │
    │  │             服务层                       │  │
    │  │  • 市场数据服务 (akshare, BaoStock)     │  │
    │  │  • 公司信息服务                         │  │
    │  │  • 数据库服务                           │  │
    │  └─────────────────────────────────────────┘  │
    │  ┌─────────────────────────────────────────┐  │
    │  │             核心层                       │  │
    │  │  • 数据模型 (Pydantic)                  │  │
    │  │  • 配置管理                             │  │
    │  │  • 异常处理                             │  │
    │  │  • 常量定义                             │  │
    │  └─────────────────────────────────────────┘  │
    │  ┌─────────────────────────────────────────┐  │
    │  │             工具层                       │  │
    │  │  • 日志配置                             │  │
    │  │  • 数据验证                             │  │
    │  │  • 辅助函数                             │  │
    │  │  • 可视化工具                           │  │
    │  └─────────────────────────────────────────┘  │
    └─────────────────┬─────────────────────────────┘
                      │
    ┌─────────────────▼─────────────────────────────┐
    │               数据源层                         │
    │  • akshare (实时行情)                         │
    │  • BaoStock (历史数据)                        │
    │  • JQData (聚宽数据)                          │
    │  • 东方财富 API                               │
    └─────────────────┬─────────────────────────────┘
                      │
    ┌─────────────────▼─────────────────────────────┐
    │               数据存储层                       │
    │  • SQLite 数据库                              │
    │  • CSV 文件存储                               │
    │  • 内存缓存                                   │
    └───────────────────────────────────────────────┘
```

## 目录结构

```
YNstock/
├── src/                            # 源代码目录
│   ├── ynstock/                   # 主包
│   │   ├── api/                  # API层
│   │   │   ├── routers/          # HTTP路由
│   │   │   └── websocket/        # WebSocket处理
│   │   ├── core/                 # 核心模块
│   │   ├── services/             # 服务层
│   │   │   ├── market/          # 市场数据服务
│   │   │   ├── company/         # 公司信息服务
│   │   │   └── database/        # 数据库服务
│   │   ├── utils/               # 工具函数
│   │   └── main.py             # 应用入口
│   └── scripts/                # 脚本目录
├── tests/                      # 测试目录
├── data/                       # 数据目录
├── config/                     # 配置文件
├── docs/                       # 文档
└── pyproject.toml             # 项目配置
```

## 核心模块详解

### 1. API 层

#### HTTP 路由
- `routers/market.py`: 行情数据相关API
- `routers/stock.py`: 股票数据相关API
- `routers/company.py`: 公司信息相关API

#### WebSocket 处理器
- `websocket/handlers.py`: WebSocket连接管理
- `websocket/manager.py`: 连接管理器
- `websocket/clients/`: 数据源客户端

### 2. 服务层

#### 市场数据服务
- `services/market/akshare.py`: akshare数据源集成
- `services/market/baostock.py`: BaoStock数据源集成
- `services/market/jqdata.py`: 聚宽数据源集成

#### 公司信息服务
- `services/company/crawler.py`: 公司信息爬虫
- `services/company/spot.py`: 实时数据获取

#### 数据库服务
- `services/database/repository.py`: 数据访问层
- `services/database/models.py`: SQLAlchemy模型

### 3. 核心层

#### 数据模型
- `core/models.py`: Pydantic数据模型
- `core/exceptions.py`: 自定义异常类
- `core/constants.py`: 常量定义
- `core/config.py`: 配置管理

### 4. 工具层

#### 通用工具
- `utils/logger.py`: 日志配置
- `utils/validators.py`: 数据验证
- `utils/helpers.py`: 辅助函数
- `utils/visualization.py`: 可视化工具

## 数据流

### 实时数据流
```
数据源 (akshare/JQData) → WebSocket客户端 → WebSocket管理器 → 客户端
```

### 历史数据流
```
数据源 (BaoStock) → 数据采集脚本 → CSV文件 → 数据库导入 → API查询 → 客户端
```

### 公司信息流
```
数据源 (akshare/东方财富) → 爬虫服务 → CSV文件 → 数据库导入 → API查询 → 客户端
```

## 配置管理

系统支持多层配置：
1. 环境变量 (最高优先级)
2. YAML配置文件
3. 默认配置值

配置文件位于 `config/` 目录：
- `settings.yaml`: 应用配置
- `logging.yaml`: 日志配置
- `.env.example`: 环境变量示例

## 数据存储

### 数据库
- 使用 SQLite 作为主要数据库
- 数据库文件位置: `data/database/ynstock.db`
- 支持 SQLAlchemy ORM

### 文件存储
- 原始数据: `data/raw/` (CSV格式)
- 处理后的数据: `data/processed/`
- 日志文件: `logs/`

## 扩展性设计

### 添加新数据源
1. 在 `services/market/` 下创建新的数据源服务
2. 实现统一的接口方法
3. 在配置中启用数据源

### 添加新的API端点
1. 在 `api/routers/` 下创建新的路由模块
2. 注册路由到主应用
3. 添加相应的服务调用

### 添加新的数据模型
1. 在 `core/models.py` 中添加Pydantic模型
2. 在 `services/database/models.py` 中添加SQLAlchemy模型
3. 更新数据库迁移脚本

## 部署架构

### 开发环境
- 单进程 FastAPI 服务器
- 本地 SQLite 数据库
- 文件系统存储

### 生产环境建议
- 使用 uvicorn 或 gunicorn 多进程部署
- 考虑使用 PostgreSQL 或 MySQL 替代 SQLite
- 添加 Redis 缓存层
- 使用 Nginx 作为反向代理
- 配置 HTTPS 加密

## 监控和日志

### 日志系统
- 结构化日志记录
- 多级别日志输出 (DEBUG, INFO, WARNING, ERROR)
- 日志轮转和归档

### 健康检查
- HTTP 健康检查端点
- 数据库连接检查
- 数据源可用性检查

## 安全性考虑

### API 安全
- 请求速率限制
- 输入验证和消毒
- CORS 配置

### 数据安全
- 敏感配置使用环境变量
- 数据库连接加密
- 文件权限控制

### WebSocket 安全
- 连接认证
- 消息验证
- 防止 DoS 攻击

## 性能优化

### 缓存策略
- 内存缓存频繁查询的数据
- 数据库查询优化
- 文件系统缓存

### 并发处理
- 异步 I/O 操作
- 连接池管理
- 批量数据处理

## 未来扩展方向

1. **分布式部署**: 支持多节点部署和负载均衡
2. **数据管道**: 添加 ETL 数据处理管道
3. **机器学习**: 集成股票预测模型
4. **移动端支持**: 提供移动应用 API
5. **实时计算**: 添加实时指标计算引擎