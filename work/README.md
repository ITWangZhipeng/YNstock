# 股票数据处理项目

## 项目概述
这是一个基于Python的股票数据分析项目，包含SQLite数据库导入和多种数据源获取功能。

## 文件说明

### 数据库相关文件
- `to_sqlite.py` - 将CSV文件导入SQLite数据库的主要脚本
- `stock_data.db` - 生成的SQLite数据库文件
- `database_import.log` - 数据库导入过程的日志文件

### BaoStock数据获取文件
- `baostock_fetcher.py` - 完整的BaoStock数据获取类，支持多种数据查询
- `baostock_simple_demo.py` - BaoStock快速入门示例

### 测试文件
- `simple_test.py` - SQLite数据库简单验证脚本
- `test_database.py` - 数据库功能完整测试脚本

## 功能特性

### SQLite数据库导入
- 自动读取`compony/csv`目录下的CSV文件
- 创建股票基本信息表和实时数据表
- 支持数据清洗和类型转换
- 建立索引优化查询性能

### BaoStock数据获取
- 支持股票基本信息查询
- 历史K线数据获取（日线、周线、月线等）
- 财务指标数据查询
- A股股票列表获取
- 自动处理数据类型转换

## 使用方法

### 运行数据库导入
```bash
cd work
python to_sqlite.py
```

### 测试数据库
```bash
python simple_test.py
```

### 使用BaoStock获取数据
```bash
# 安装baostock（如果网络允许）
pip install baostock

# 运行示例
python baostock_simple_demo.py
```

## 数据表结构

### stock_basic (股票基本信息表)
- id: 主键
- stock_code: 股票代码
- stock_name: 股票名称
- company_name: 公司名称
- listing_date: 上市日期

### stock_realtime (股票实时数据表)
- id: 主键
- stock_code: 股票代码
- stock_name: 股票名称
- total_market_value: 总市值
- sector: 所属板块
- sw_industry: 申万一级行业
- main_net_inflow: 主力净流入
- latest_price: 最新价

## 注意事项
1. 确保已安装所需依赖：pandas, sqlite3
2. BaoStock可能需要网络连接才能正常使用
3. CSV文件需要位于指定目录结构中
4. 数据库文件会自动创建在运行目录下

## 依赖库
- pandas >= 3.0.1
- sqlite3 (Python标准库)
- baostock (可选，用于实时数据获取)
- akshare (项目原有依赖)