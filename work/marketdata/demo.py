from jqdata import *


def initialize(context):
    # 设定要操作的股票
    g.security = '000001.XSHE'

    # 设置基准
    set_benchmark('000300.XSHG')

    # 开启动态复权
    set_option('use_real_price', True)

    # 日志输出
    log.info("策略初始化完成")


# 方法1：使用 on_bar 回调 (推荐，系统会自动按频率推送)
# 注意：需要在策略配置中选择频率为 "1m"
def on_bar(context, bars):
    """
    bars: 当前分钟的行情数据对象
    """
    security = g.security

    # 检查当前标的是否在bars中 (防止停牌等情况)
    if security not in bars.index:
        return

    current_data = bars[security]

    # 获取当前分钟的开盘、收盘、最高、最低、成交量
    open_price = current_data.open
    close_price = current_data.close
    high_price = current_data.high
    low_price = current_data.low
    volume = current_data.volume

    log.info(f"时间: {current_data.time}, 代码: {security}, 现价: {close_price}, 成交量: {volume}")

    # --- 在此处编写你的交易逻辑 ---
    # 例如：如果收盘价大于开盘价，则买入
    # if close_price > open_price:
    #     order_target(security, 100)


# 方法2：如果你必须在策略中主动查询“过去N分钟”的数据用于计算指标
def handle_data(context, data):
    # 仅在交易时段运行，避免非交易时间报错
    if context.current_dt.hour < 9 or (context.current_dt.hour == 9 and context.current_dt.minute < 30):
        return

    # 获取过去 5 分钟的 1分钟K线数据 (用于计算均线等)
    # count: 获取多少根K线
    # unit: 时间单位 '1m'
    h_bars = attribute_history(g.security, count=5, unit='1m', fields=['close', 'volume'])

    if len(h_bars) < 5:
        return

    # 计算简单的5分钟均价
    avg_price = h_bars['close'].mean()
    log.info(f"过去5分钟均价: {avg_price}")