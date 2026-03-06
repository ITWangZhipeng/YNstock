"""数据访问层"""
from typing import Optional, List, Dict, Any
import sqlite3
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseRepository:
    """数据库仓库基类"""

    def __init__(self, db_path: str = "stock_data.db"):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """连接到数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            return False

    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """执行查询语句"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            return []

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """执行更新语句"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            return False

class StockRepository(DatabaseRepository):
    """股票数据仓库"""

    def get_stock_by_code(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """根据股票代码获取股票基本信息"""
        query = """
            SELECT stock_code, stock_name, company_name, listing_date
            FROM stock_basic
            WHERE stock_code = ?
        """
        results = self.execute_query(query, (stock_code,))
        if results:
            row = results[0]
            return {
                "stock_code": row[0],
                "stock_name": row[1],
                "company_name": row[2],
                "listing_date": row[3]
            }
        return None

    def get_stock_realtime_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票实时数据"""
        query = """
            SELECT stock_code, stock_name, total_market_value, sector,
                   sw_industry, main_net_inflow, latest_price, created_at
            FROM stock_realtime
            WHERE stock_code = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        results = self.execute_query(query, (stock_code,))
        if results:
            row = results[0]
            return {
                "stock_code": row[0],
                "stock_name": row[1],
                "total_market_value": row[2],
                "sector": row[3],
                "sw_industry": row[4],
                "main_net_inflow": row[5],
                "latest_price": row[6],
                "created_at": row[7]
            }
        return None

    def search_stocks_by_name(self, name_keyword: str) -> List[Dict[str, Any]]:
        """根据股票名称关键词搜索股票"""
        query = """
            SELECT stock_code, stock_name, company_name
            FROM stock_basic
            WHERE stock_name LIKE ? OR company_name LIKE ?
            LIMIT 50
        """
        keyword = f"%{name_keyword}%"
        results = self.execute_query(query, (keyword, keyword))
        return [
            {
                "stock_code": row[0],
                "stock_name": row[1],
                "company_name": row[2]
            }
            for row in results
        ]