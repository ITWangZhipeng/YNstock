import baostock as bs
import pandas as pd
import os
from datetime import datetime, timedelta

def get_market_prefix(stock_code):
    """
    根据股票代码判断市场前缀
    沪市：600、601、603等开头 -> sh.
    深市：000、002等开头 -> sz.
    """
    if stock_code.startswith(('600', '601', '603', '605', '688')):
        return f"sh.{stock_code}"
    elif stock_code.startswith(('000', '002', '300')):
        return f"sz.{stock_code}"
    else:
        return None

def get_one_year_data(stock_code_with_prefix):
    """
    获取单只股票近一年的分钟数据
    """
    # 计算一年前的日期
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    print(f"正在获取 {stock_code_with_prefix} 从 {start_date} 到 {end_date} 的数据...")

    # 查询分钟数据
    rs = bs.query_history_k_data_plus(stock_code_with_prefix,
                                      "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                      start_date=start_date,
                                      end_date=end_date,
                                      frequency="5",
                                      adjustflag="3")

    if rs.error_code != '0':
        print(f"查询错误: {rs.error_code}, {rs.error_msg}")
        return None

    # 获取数据
    data_list = []
    while (rs.error_code == '0') and rs.next():
        data_list.append(rs.get_row_data())

    if not data_list:
        print(f"未获取到 {stock_code_with_prefix} 的数据")
        return None

    result = pd.DataFrame(data_list, columns=rs.fields)
    return result

def batch_get_stock_minute_data():
    """
    批量获取股票分钟数据
    """
    # 登陆系统
    lg = bs.login()
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    if lg.error_code != '0':
        print("登录失败，退出程序")
        return

    try:
        # 读取股票代码CSV文件
        csv_file_path = '../../../data/raw/company/股票代码+名称.csv'
        if not os.path.exists(csv_file_path):
            print(f"找不到CSV文件: {csv_file_path}")
            return

        stock_df = pd.read_csv(csv_file_path)
        print(f"共找到 {len(stock_df)} 只股票")

        # 创建输出目录
        output_dir = '../../../data/raw/market'
        os.makedirs(output_dir, exist_ok=True)

        success_count = 0
        error_count = 0

        # 遍历股票代码
        for index, row in stock_df.iterrows():
            stock_code = row['股票代码']
            stock_name = row['股票名称']

            # 获取带市场前缀的股票代码
            stock_code_with_prefix = get_market_prefix(str(stock_code).zfill(6))

            if stock_code_with_prefix is None:
                print(f"无法识别股票代码格式: {stock_code}")
                error_count += 1
                continue

            try:
                # 获取数据
                result_df = get_one_year_data(stock_code_with_prefix)

                if result_df is not None and not result_df.empty:
                    # 保存到CSV文件，使用股票代码命名
                    output_file = os.path.join(output_dir, f"{stock_code_with_prefix}.csv")
                    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"已保存 {stock_code} ({stock_name}) 的数据到 {output_file}")
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                print(f"处理股票 {stock_code} 时出错: {str(e)}")
                error_count += 1
                continue

            # 添加延迟避免请求过于频繁
            # time.sleep(0.1)

        print(f"\n批量处理完成!")
        print(f"成功处理: {success_count} 只股票")
        print(f"处理失败: {error_count} 只股票")

    finally:
        # 登出系统
        bs.logout()
        print("已登出系统")

if __name__ == "__main__":
    batch_get_stock_minute_data()