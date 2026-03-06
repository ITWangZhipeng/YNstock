"""SQLAlchemy 数据模型"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class StockBasic(Base):
    """股票基本信息表"""
    __tablename__ = 'stock_basic'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), unique=True, nullable=False, index=True)
    stock_name = Column(String(50), nullable=False)
    company_name = Column(String(100))
    listing_date = Column(String(10))  # YYYY-MM-DD格式
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    realtime_data = relationship("StockRealtime", back_populates="stock")

class StockRealtime(Base):
    """股票实时数据表"""
    __tablename__ = 'stock_realtime'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey('stock_basic.stock_code'), nullable=False, index=True)
    stock_name = Column(String(50), nullable=False)
    total_market_value = Column(Float)  # 总市值
    sector = Column(String(50))  # 所属板块
    sw_industry = Column(String(50))  # 申万一级行业
    main_net_inflow = Column(Float)  # 主力净流入
    latest_price = Column(Float)  # 最新价
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    stock = relationship("StockBasic", back_populates="realtime_data")

# 创建索引
Index('idx_stock_realtime_created_at', StockRealtime.created_at)
Index('idx_stock_realtime_sector', StockRealtime.sector)