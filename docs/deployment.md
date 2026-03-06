# YNstock 部署指南

## 概述

本文档介绍如何部署 YNstock 股票行情数据服务系统。

## 环境要求

### 系统要求
- Python 3.9 或更高版本
- 内存: 至少 2GB RAM
- 磁盘空间: 至少 10GB（用于存储数据）
- 网络: 稳定的互联网连接（访问外部数据源）

### 软件依赖
- pip 包管理器
- Git（可选，用于版本控制）

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd YNstock
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -e .
```

安装开发依赖（可选）：
```bash
pip install -e ".[dev]"
```

### 4. 配置环境变量

复制环境变量示例文件：
```bash
cp config/.env.example config/.env
```

编辑 `config/.env` 文件，设置必要的配置：
```bash
# 聚宽账户配置（必需）
JQDATA_USERNAME=your_username
JQDATA_PASSWORD=your_password

# 服务器配置（可选）
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 日志配置（可选）
LOG_LEVEL=INFO
```

### 5. 创建数据目录

```bash
mkdir -p data/raw/company data/raw/market data/processed data/database logs
```

### 6. 运行数据库初始化脚本（可选）

如果需要导入示例数据：
```bash
python -m src.scripts.db.import_data
```

### 7. 启动服务

```bash
python -m src.ynstock.main
```

或者使用 uvicorn：
```bash
uvicorn src.ynstock.main:app --host 0.0.0.0 --port 8000 --reload
```

### 8. 验证部署

访问以下地址验证服务是否正常运行：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/get/k
- WebSocket 测试: ws://localhost:8000/ws/market-data

## 生产环境部署

### 1. 使用 Gunicorn（Linux/Mac）

安装 Gunicorn：
```bash
pip install gunicorn
```

使用 Gunicorn 启动服务：
```bash
gunicorn src.ynstock.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

参数说明：
- `-w 4`: 4个工作进程
- `-k uvicorn.workers.UvicornWorker`: 使用 uvicorn worker
- `-b 0.0.0.0:8000`: 绑定地址和端口

### 2. 使用系统服务（Systemd）

创建 systemd 服务文件 `/etc/systemd/system/ynstock.service`：

```ini
[Unit]
Description=YNstock Stock Data Service
After=network.target

[Service]
User=ynstock
Group=ynstock
WorkingDirectory=/opt/ynstock
Environment="PATH=/opt/ynstock/.venv/bin"
EnvironmentFile=/opt/ynstock/config/.env
ExecStart=/opt/ynstock/.venv/bin/gunicorn src.ynstock.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ynstock
sudo systemctl start ynstock
```

查看服务状态：
```bash
sudo systemctl status ynstock
```

### 3. 使用 Docker

创建 Dockerfile：
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml .
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/

# 安装Python依赖
RUN pip install --no-cache-dir -e .

# 创建数据目录
RUN mkdir -p data/raw/company data/raw/market data/processed data/database logs

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.ynstock.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建并运行 Docker 容器：
```bash
# 构建镜像
docker build -t ynstock .

# 运行容器
docker run -d \
  --name ynstock \
  -p 8000:8000 \
  -v ./config/.env:/app/config/.env \
  -v ./data:/app/data \
  ynstock
```

### 4. 使用 Docker Compose

创建 `docker-compose.yml`：
```yaml
version: '3.8'

services:
  ynstock:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JQDATA_USERNAME=${JQDATA_USERNAME}
      - JQDATA_PASSWORD=${JQDATA_PASSWORD}
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: always
```

启动服务：
```bash
docker-compose up -d
```

## 配置详解

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| JQDATA_USERNAME | (无) | 聚宽用户名（必需） |
| JQDATA_PASSWORD | (无) | 聚宽密码（必需） |
| SERVER_HOST | 0.0.0.0 | 服务器监听地址 |
| SERVER_PORT | 8000 | 服务器端口 |
| LOG_LEVEL | INFO | 日志级别 |
| DATABASE_URL | sqlite:///data/database/ynstock.db | 数据库连接URL |
| DATA_DIR | ./data | 数据目录根路径 |

### YAML 配置文件

主要配置文件 `config/settings.yaml` 支持以下配置项：

```yaml
# 应用配置
app:
  name: "YNstock"
  version: "0.1.0"
  debug: false

# 服务器配置
server:
  host: "0.0.0.0"
  port: 8000
  reload: false  # 生产环境设置为 false

# 数据源配置
data_sources:
  jqdata:
    enabled: true
  baostock:
    enabled: true
  akshare:
    enabled: true

# WebSocket配置
websocket:
  heartbeat_interval: 30
  max_connections: 100
  timeout: 60

# 数据库配置
database:
  url: "sqlite:///data/database/ynstock.db"
  echo: false  # 生产环境设置为 false
```

## 数据管理

### 数据库备份

```bash
# 备份 SQLite 数据库
cp data/database/ynstock.db data/database/ynstock.db.backup.$(date +%Y%m%d)

# 恢复数据库
cp data/database/ynstock.db.backup.20240101 data/database/ynstock.db
```

### 数据清理

```bash
# 清理日志文件（保留最近30天）
find logs/ -name "*.log" -mtime +30 -delete

# 清理临时文件
find data/processed/ -name "*.tmp" -delete
```

## 监控和维护

### 日志查看

```bash
# 查看应用日志
tail -f logs/ynstock.log

# 查看错误日志
tail -f logs/error.log

# 查看系统服务日志
sudo journalctl -u ynstock -f
```

### 健康检查

```bash
# 检查服务是否运行
curl -f http://localhost:8000/get/k

# 检查数据库连接
curl http://localhost:8000/api/stock-files
```

### 性能监控

```bash
# 查看内存使用
ps aux | grep ynstock

# 查看网络连接
netstat -an | grep :8000
```

## 安全配置

### 防火墙设置

```bash
# 允许8000端口
sudo ufw allow 8000/tcp

# 限制访问IP（可选）
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

### HTTPS 配置（使用 Nginx）

安装 Nginx：
```bash
sudo apt install nginx
```

创建 Nginx 配置文件 `/etc/nginx/sites-available/ynstock`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书路径
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

启用配置并重启 Nginx：
```bash
sudo ln -s /etc/nginx/sites-available/ynstock /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 获取 SSL 证书（Let's Encrypt）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口是否被占用：`netstat -tulpn | grep :8000`
   - 检查环境变量是否设置正确
   - 查看日志文件获取详细错误信息

2. **数据库连接错误**
   - 检查数据库文件权限
   - 确保数据目录存在
   - 检查磁盘空间

3. **数据源连接失败**
   - 检查网络连接
   - 验证 API 密钥和账户信息
   - 查看数据源服务状态

4. **内存不足**
   - 减少工作进程数量
   - 增加系统内存
   - 优化数据缓存策略

### 调试模式

临时启用调试模式：
```bash
export LOG_LEVEL=DEBUG
python -m src.ynstock.main
```

## 升级指南

### 备份数据
```bash
# 备份数据库
cp data/database/ynstock.db data/database/ynstock.db.backup.upgrade

# 备份配置文件
cp -r config/ config.backup/
```

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -e .
```

### 重启服务
```bash
sudo systemctl restart ynstock
```

## 扩展部署

### 多节点部署

对于高可用性要求，可以考虑多节点部署：

1. **负载均衡**: 使用 Nginx 或 HAProxy 作为负载均衡器
2. **共享存储**: 使用网络文件系统（NFS）或对象存储共享数据
3. **会话管理**: 使用 Redis 存储 WebSocket 会话状态
4. **数据库集群**: 考虑使用 PostgreSQL 集群

### 云平台部署

#### AWS
- 使用 EC2 运行应用
- 使用 RDS 作为数据库
- 使用 S3 存储数据文件
- 使用 ELB 作为负载均衡器

#### Azure
- 使用 Azure App Service
- 使用 Azure SQL Database
- 使用 Azure Storage
- 使用 Azure Load Balancer

#### Google Cloud
- 使用 Compute Engine
- 使用 Cloud SQL
- 使用 Cloud Storage
- 使用 Load Balancing

## 支持与帮助

- 查看详细文档：`docs/` 目录
- 报告问题：项目 issue 跟踪
- 社区支持：项目讨论区

## 版本历史

- v0.1.0: 初始版本，支持基本功能
- （后续版本更新记录）