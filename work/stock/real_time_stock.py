import akshare as ak
import pandas as pd
import time
from datetime import datetime
import threading

# ===================== 配置区（请根据你的需求修改）=====================
TARGET_STOCK_CODE = "600519"  # 监控的股票代码（例：贵州茅台 600519）
SAVE_INTERVAL = 5  # 数据保存间隔（秒）
CSV_SAVE_PATH = "real_time_order_data.csv"  # 数据保存路径
# =====================================================================

# 初始化全局数据存储
order_data_list = []
is_running = True


def get_realtime_order_data(stock_code):
    """
    获取单只股票的实时报单数据（五档盘口+最新成交）
    """
    try:
        # 获取实时行情快照（包含盘口、成交等核心报单数据）
        stock_spot_df = ak.stock_zh_a_spot_em()
        # 筛选目标股票
        stock_data = stock_spot_df[stock_spot_df["代码"] == stock_code].iloc[0]

        # 构造标准化的报单数据字典
        order_data = {
            "时间戳": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # 精确到毫秒
            "股票代码": stock_code,
            "股票名称": stock_data["名称"],
            "最新价": stock_data["最新价"],
            "涨跌幅": stock_data["涨跌幅"],
            # 买盘报单
            "买一价": stock_data["买一价"],
            "买一量": stock_data["买一量"],
            "买二价": stock_data["买二价"],
            "买二量": stock_data["买二量"],
            "买三价": stock_data["买三价"],
            "买三量": stock_data["买三量"],
            # 卖盘报单
            "卖一价": stock_data["卖一价"],
            "卖一量": stock_data["卖一量"],
            "卖二价": stock_data["卖二价"],
            "卖二量": stock_data["卖二量"],
            "卖三价": stock_data["卖三价"],
            "卖三量": stock_data["卖三量"],
            # 成交数据
            "成交量": stock_data["成交量"],
            "成交额": stock_data["成交额"],
            "换手率": stock_data["换手率"]
        }
        return order_data
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None


def save_data_to_csv():
    """
    定时将数据保存到CSV文件（避免频繁IO）
    """
    global order_data_list
    while is_running:
        time.sleep(SAVE_INTERVAL)
        if order_data_list:
            # 将列表转为DataFrame
            df = pd.DataFrame(order_data_list)
            # 追加写入CSV（无文件则创建，有则追加，不重复写表头）
            df.to_csv(CSV_SAVE_PATH, mode='a', header=not pd.io.common.file_exists(CSV_SAVE_PATH), index=False,
                      encoding='utf-8-sig')
            # 清空已保存的数据
            order_data_list = []
            print(f"[{datetime.now()}] 已保存 {len(df)} 条报单数据到 {CSV_SAVE_PATH}")


def main_monitor():
    """
    主监控函数：循环获取数据并缓存
    """
    global order_data_list, is_running
    print(f"===== 开始监控股票 {TARGET_STOCK_CODE} 实时报单数据 =====")
    print(f"数据将每{SAVE_INTERVAL}秒保存一次，按 Ctrl+C 停止监控\n")

    # 启动数据保存线程
    save_thread = threading.Thread(target=save_data_to_csv, daemon=True)
    save_thread.start()

    try:
        while is_running:
            # 获取实时报单数据
            order_data = get_realtime_order_data(TARGET_STOCK_CODE)
            if order_data:
                order_data_list.append(order_data)
                # 打印实时数据（便于观察）
                print(
                    f"\r[{order_data['时间戳']}] {order_data['股票名称']} | 最新价: {order_data['最新价']} | 买一: {order_data['买一价']}/{order_data['买一量']} | 卖一: {order_data['卖一价']}/{order_data['卖一量']}",
                    end="")
            # 控制获取频率（默认0.5秒一次，避免请求过快）
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n\n===== 停止监控 =====")
        is_running = False
        # 等待保存线程完成最后一次保存
        save_thread.join()
        print("监控结束，所有数据已保存完成！")


if __name__ == "__main__":
    # 安装依赖（首次运行请取消注释执行）
    # !pip install akshare pandas

    # 运行主监控程序
    main_monitor()