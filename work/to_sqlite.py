import sqlite3
import pandas as pd
import os
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_import.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockDataToSQLite:
    def __init__(self, db_path="stock_data.db", csv_directory="./company/csv"):
        """
        初始化数据库导入器
        
        Args:
            db_path (str): SQLite数据库文件路径
            csv_directory (str): CSV文件所在目录
        """
        self.db_path = db_path
        self.csv_directory = Path(csv_directory)
        self.connection = None
        
    def connect_database(self):
        """连接到SQLite数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            logger.info(f"成功连接到数据库: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            return False
    
    def close_database(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def create_tables(self):
        """创建数据表"""
        try:
            cursor = self.connection.cursor()
            
            # 创建股票基本信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_basic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT UNIQUE NOT NULL,
                    stock_name TEXT NOT NULL,
                    company_name TEXT,
                    listing_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建股票实时数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_realtime (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    total_market_value REAL,
                    sector TEXT,
                    sw_industry TEXT,
                    main_net_inflow REAL,
                    latest_price REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_code) REFERENCES stock_basic (stock_code)
                )
            ''')
            
            # 创建索引提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON stock_basic(stock_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code_rt ON stock_realtime(stock_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector ON stock_realtime(sector)')
            
            self.connection.commit()
            logger.info("数据表创建成功")
            return True
            
        except Exception as e:
            logger.error(f"创建数据表失败: {e}")
            return False
    
    def import_stock_codes(self, csv_file):
        """导入股票代码和名称数据"""
        try:
            file_path = self.csv_directory / csv_file
            if not file_path.exists():
                logger.warning(f"CSV文件不存在: {file_path}")
                return False
                
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            logger.info(f"读取CSV文件: {csv_file}, 共 {len(df)} 条记录")
            
            # 数据清洗
            df = df.dropna(subset=['股票代码', '股票名称'])
            df['股票代码'] = df['股票代码'].astype(str).str.zfill(6)  # 确保股票代码为6位
            
            # 插入数据
            cursor = self.connection.cursor()
            inserted_count = 0
            
            for _, row in df.iterrows():
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO stock_basic (stock_code, stock_name)
                        VALUES (?, ?)
                    ''', (row['股票代码'], row['股票名称']))
                    inserted_count += 1
                except Exception as e:
                    logger.warning(f"插入记录失败 ({row['股票代码']}): {e}")
            
            self.connection.commit()
            logger.info(f"成功导入 {inserted_count} 条股票代码记录")
            return True
            
        except Exception as e:
            logger.error(f"导入股票代码数据失败: {e}")
            return False
    
    def import_realtime_data(self, csv_file):
        """导入股票实时数据"""
        try:
            file_path = self.csv_directory / csv_file
            if not file_path.exists():
                logger.warning(f"CSV文件不存在: {file_path}")
                return False
                
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            logger.info(f"读取CSV文件: {csv_file}, 共 {len(df)} 条记录")
            
            # 数据清洗和类型转换
            df = df.dropna(subset=['股票代码', '股票名称'])
            df['股票代码'] = df['股票代码'].astype(str).str.zfill(6)
            
            # 处理数值型字段
            numeric_columns = ['总市值', '主力净流入', '最新价']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 插入数据
            cursor = self.connection.cursor()
            inserted_count = 0
            
            for _, row in df.iterrows():
                try:
                    cursor.execute('''
                        INSERT INTO stock_realtime (
                            stock_code, stock_name, total_market_value, 
                            sector, sw_industry, main_net_inflow, latest_price
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['股票代码'],
                        row['股票名称'],
                        float(row.get('总市值', 0)),
                        str(row.get('所属板块', '')),
                        str(row.get('申万一级行业', '')),
                        float(row.get('主力净流入', 0)),
                        float(row.get('最新价', 0))
                    ))
                    inserted_count += 1
                except Exception as e:
                    logger.warning(f"插入实时数据失败 ({row['股票代码']}): {e}")
            
            self.connection.commit()
            logger.info(f"成功导入 {inserted_count} 条实时数据记录")
            return True
            
        except Exception as e:
            logger.error(f"导入实时数据失败: {e}")
            return False
    
    def get_table_info(self):
        """获取数据库表信息"""
        try:
            cursor = self.connection.cursor()
            
            # 获取表结构信息
            tables = ['stock_basic', 'stock_realtime']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"表 {table}: {count} 条记录")
                
                # 显示前几条记录作为示例
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                if rows:
                    logger.info(f"{table} 表示例数据:")
                    for row in rows:
                        logger.info(f"  {row}")
                        
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
    
    def run_import(self):
        """执行完整的数据导入流程"""
        logger.info("开始导入CSV数据到SQLite数据库...")
        
        # 连接数据库
        if not self.connect_database():
            return False
        
        try:
            # 创建表结构
            if not self.create_tables():
                return False
            
            # 导入股票代码数据
            stock_code_file = "股票代码+名称.csv"
            self.import_stock_codes(stock_code_file)
            
            # 导入实时数据
            realtime_file = "实时市值+所属板块.csv"
            self.import_realtime_data(realtime_file)
            
            # 显示导入结果
            self.get_table_info()
            
            logger.info("数据导入完成！")
            return True
            
        except Exception as e:
            logger.error(f"数据导入过程中发生错误: {e}")
            return False
        finally:
            self.close_database()

def main():
    """主函数"""
    # 设置数据库路径和CSV目录
    db_path = "stock_data.db"
    csv_directory = "./company/csv"
    
    # 创建导入器实例
    importer = StockDataToSQLite(db_path=db_path, csv_directory=csv_directory)
    
    # 执行导入
    success = importer.run_import()
    
    if success:
        logger.info(f"数据库已成功创建: {db_path}")
        logger.info("可以使用以下方式访问数据:")
        logger.info("1. 使用 sqlite3 命令行工具")
        logger.info("2. 在Python中使用 sqlite3 模块")
        logger.info("3. 使用数据库管理工具如 DB Browser for SQLite")
    else:
        logger.error("数据导入失败，请检查日志文件获取详细信息")

if __name__ == "__main__":
    main()