import baostock as bs
import pandas as pd
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaoStockDataFetcher:
    def __init__(self):
        """初始化BaoStock数据获取器"""
        self.lg = None
        
    def login(self):
        """登录BaoStock系统"""
        try:
            self.lg = bs.login()
            if self.lg.error_code == '0':
                logger.info("BaoStock登录成功")
                return True
            else:
                logger.error(f"BaoStock登录失败: {self.lg.error_msg}")
                return False
        except Exception as e:
            logger.error(f"登录过程出错: {e}")
            return False
    
    def logout(self):
        """退出BaoStock系统"""
        if self.lg:
            bs.logout()
            logger.info("BaoStock已退出")
    
    def get_stock_basic_info(self, stock_code):
        """
        获取单只股票基本信息
        
        Args:
            stock_code (str): 股票代码，格式如：sh.600000 或 sz.000001
            
        Returns:
            dict: 股票基本信息
        """
        try:
            rs = bs.query_stock_basic(code=stock_code)
            if rs.error_code == '0':
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                if data_list:
                    result = {
                        'code': data_list[0][0],
                        'name': data_list[0][2],
                        'ipo_date': data_list[0][3],
                        'out_date': data_list[0][4],
                        'type': data_list[0][5],
                        'status': data_list[0][6]
                    }
                    return result
                else:
                    logger.warning(f"未找到股票 {stock_code} 的基本信息")
                    return None
            else:
                logger.error(f"查询股票基本信息失败: {rs.error_msg}")
                return None
        except Exception as e:
            logger.error(f"获取股票基本信息出错: {e}")
            return None
    
    def get_history_k_data(self, stock_code, start_date=None, end_date=None, frequency="d", adjustflag="3"):
        """
        获取历史K线数据
        
        Args:
            stock_code (str): 股票代码
            start_date (str): 开始日期，格式：YYYY-MM-DD
            end_date (str): 结束日期，格式：YYYY-MM-DD
            frequency (str): 数据类型，默认为d，日k线；d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据
            adjustflag (str): 复权类型，默认前复权，1：后复权，2：前复权，3：不复权
            
        Returns:
            pandas.DataFrame: K线数据
        """
        try:
            # 如果没有指定日期，默认获取最近一年的数据
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                stock_code,
                "date,code,open,high,low,close,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjustflag=adjustflag
            )
            
            if rs.error_code == '0':
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                if data_list:
                    result = pd.DataFrame(data_list, columns=rs.fields)
                    # 数据类型转换
                    numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount', 
                                     'turn', 'pctChg', 'peTTM', 'pbMRQ', 'psTTM', 'pcfNcfTTM']
                    for col in numeric_columns:
                        if col in result.columns:
                            result[col] = pd.to_numeric(result[col], errors='coerce')
                    
                    result['date'] = pd.to_datetime(result['date'])
                    return result
                else:
                    logger.warning(f"未获取到 {stock_code} 的历史数据")
                    return pd.DataFrame()
            else:
                logger.error(f"查询历史数据失败: {rs.error_msg}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取历史K线数据出错: {e}")
            return pd.DataFrame()
    
    def get_stock_indicators(self, stock_code, date=None):
        """
        获取股票财务指标
        
        Args:
            stock_code (str): 股票代码
            date (str): 日期，格式：YYYY-MM-DD
            
        Returns:
            pandas.DataFrame: 财务指标数据
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                stock_code,
                "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                start_date=date,
                end_date=date,
                frequency="d",
                adjustflag="3"
            )
            
            if rs.error_code == '0':
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                if data_list:
                    result = pd.DataFrame(data_list, columns=rs.fields)
                    return result
                else:
                    logger.warning(f"未获取到 {stock_code} 的财务指标")
                    return pd.DataFrame()
            else:
                logger.error(f"查询财务指标失败: {rs.error_msg}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取财务指标出错: {e}")
            return pd.DataFrame()
    
    def get_all_stock_list(self):
        """
        获取所有A股股票列表
        
        Returns:
            pandas.DataFrame: 股票列表
        """
        try:
            rs = bs.query_all_stock(day=datetime.now().strftime('%Y-%m-%d'))
            if rs.error_code == '0':
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                if data_list:
                    result = pd.DataFrame(data_list, columns=rs.fields)
                    return result
                else:
                    logger.warning("未获取到股票列表")
                    return pd.DataFrame()
            else:
                logger.error(f"查询股票列表失败: {rs.error_msg}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取股票列表出错: {e}")
            return pd.DataFrame()

def main():
    """主函数示例"""
    # 创建数据获取器实例
    fetcher = BaoStockDataFetcher()
    
    # 登录
    if not fetcher.login():
        return
    
    try:
        # 示例：获取平安银行的基本信息
        stock_code = "sh.600000"  # 平安银行
        print(f"\n=== 获取股票 {stock_code} 基本信息 ===")
        basic_info = fetcher.get_stock_basic_info(stock_code)
        if basic_info:
            for key, value in basic_info.items():
                print(f"{key}: {value}")
        
        # 示例：获取历史K线数据
        print(f"\n=== 获取股票 {stock_code} 最近30天K线数据 ===")
        k_data = fetcher.get_history_k_data(stock_code, 
                                          start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        if not k_data.empty:
            print(f"获取到 {len(k_data)} 条记录")
            print(k_data.tail())
        
        # 示例：获取财务指标
        print(f"\n=== 获取股票 {stock_code} 财务指标 ===")
        indicators = fetcher.get_stock_indicators(stock_code)
        if not indicators.empty:
            print(indicators)
        
        # 示例：获取股票列表
        print(f"\n=== 获取A股股票列表 ===")
        stock_list = fetcher.get_all_stock_list()
        if not stock_list.empty:
            print(f"总共 {len(stock_list)} 只股票")
            print(stock_list.head(10))
            
    finally:
        # 退出登录
        fetcher.logout()

if __name__ == "__main__":
    main()