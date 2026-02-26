# work/stock/batch_fetch_stock_data.py
import pandas as pd
import os
import time
import logging
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import baostock as bs
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_fetch_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def determine_market_prefix(stock_code):
    """
    根据股票代码判断市场前缀
    沪市：6开头 -> sh.
    深市：0或3开头 -> sz.
    北交所：8开头 -> bj.
    """
    if stock_code.startswith('6'):
        return f"sh.{stock_code}"
    elif stock_code.startswith(('0', '3')):
        return f"sz.{stock_code}"
    elif stock_code.startswith('8'):
        return f"bj.{stock_code}"
    else:
        logger.warning(f"无法识别的股票代码格式: {stock_code}")
        return None

def batch_fetch_stock_data(csv_file_path, output_dir="./stock_data", max_stocks=None, delay=1):
    """
    批量获取股票数据

    Args:
        csv_file_path (str): 股票代码CSV文件路径
        output_dir (str): 输出目录
        max_stocks (int): 最大处理股票数量，None表示处理全部
        delay (float): 请求间隔秒数，防止被限制
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 读取股票代码文件
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        logger.info(f"成功读取股票代码文件，共 {len(df)} 只股票")
    except Exception as e:
        logger.error(f"读取CSV文件失败: {e}")
        return

    # 登录BaoStock系统
    lg = bs.login()
    if lg.error_code != '0':
        logger.error(f"BaoStock登录失败: {lg.error_msg}")
        return

    logger.info(f"登录成功: {lg.error_msg}")

    success_count = 0
    fail_count = 0
    processed_count = 0

    try:
        # 遍历股票代码
        for index, row in df.iterrows():
            if max_stocks and processed_count >= max_stocks:
                break

            stock_code = str(row['股票代码']).zfill(6)  # 确保6位数字
            stock_name = row['股票名称']

            # 生成带市场前缀的代码
            market_code = determine_market_prefix(stock_code)
            if not market_code:
                fail_count += 1
                processed_count += 1
                continue

            logger.info(f"[{processed_count+1}/{len(df)}] 正在处理: {stock_code} - {stock_name} ({market_code})")

            try:
                # 参照baostock_simple_demo的方式获取历史K线数据
                rs = bs.query_history_k_data_plus(
                    market_code,
                    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                    start_date=(datetime.now() - pd.Timedelta(days=365)).strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d'),
                    frequency="d",
                    adjustflag="3"
                )

                if rs.error_code != '0':
                    logger.error(f"  ✗ 查询数据失败: {rs.error_msg}")
                    fail_count += 1
                    processed_count += 1
                    continue

                # 按照demo方式处理结果集
                data_list = []
                while (rs.error_code == '0') and rs.next():
                    data_list.append(rs.get_row_data())

                if data_list:
                    result = pd.DataFrame(data_list, columns=rs.fields)
                    # 保存为CSV文件，文件名为股票代码
                    output_file = os.path.join(output_dir, f"{stock_code}.csv")
                    result.to_csv(output_file, encoding="utf-8-sig", index=False)
                    logger.info(f"  ✓ 成功保存 {len(result)} 条记录到 {output_file}")
                    success_count += 1
                else:
                    logger.warning(f"  ⚠ 未获取到 {stock_code} 的数据")
                    fail_count += 1

            except Exception as e:
                logger.error(f"  ✗ 处理 {stock_code} 时出错: {e}")
                fail_count += 1

            processed_count += 1

            # 添加延迟防止被限制
            if delay > 0:
                time.sleep(delay)

    finally:
        # 登出系统
        bs.logout()
        logger.info("已登出BaoStock系统")

    # 输出统计信息
    logger.info("=" * 50)
    logger.info("处理完成统计:")
    logger.info(f"总计处理: {processed_count} 只股票")
    logger.info(f"成功获取: {success_count} 只")
    logger.info(f"获取失败: {fail_count} 只")
    logger.info(f"成功率: {success_count/processed_count*100:.2f}%" if processed_count > 0 else "0%")
    logger.info(f"数据保存目录: {os.path.abspath(output_dir)}")

def main():
    """主函数"""
    # CSV文件路径
    csv_file = "../company/csv/股票代码+名称.csv"

    # 输出目录
    output_dir = "./stock_data"

    # 参数设置
    max_stocks = None  # 设置为具体数字可以限制处理数量，如10只股票
    delay_seconds = 1  # 请求间隔秒数

    logger.info("开始批量获取股票数据...")
    logger.info(f"数据源: {csv_file}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"最大处理数量: {'全部' if max_stocks is None else max_stocks}")
    logger.info(f"请求间隔: {delay_seconds}秒")

    batch_fetch_stock_data(
        csv_file_path=csv_file,
        output_dir=output_dir,
        max_stocks=max_stocks,
        delay=delay_seconds
    )

if __name__ == "__main__":
    main()
