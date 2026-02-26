import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_stock_data(file_path):
    """
    加载股票历史数据
    
    Args:
        file_path (str): CSV文件路径
        
    Returns:
        pandas.DataFrame: 股票数据
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, encoding='gbk')
        print(f"成功加载数据: {len(df)} 条记录")
        print(f"数据时间范围: {df['date'].min()} 到 {df['date'].max()}")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def create_price_boxplot(df, save_path=None):
    """
    绘制价格相关字段的箱型图
    
    Args:
        df (pandas.DataFrame): 股票数据
        save_path (str): 保存路径
    """
    # 选择价格相关字段
    price_columns = ['open', 'high', 'low', 'close']
    
    # 准备数据
    price_data = df[price_columns].copy()
    price_data.columns = ['开盘价', '最高价', '最低价', '收盘价']
    
    # 创建图形
    plt.figure(figsize=(12, 8))
    
    # 绘制箱型图
    box_plot = plt.boxplot(price_data.values, 
                          labels=price_data.columns,
                          patch_artist=True,
                          notch=True,
                          showmeans=True,
                          meanprops={'marker':'D', 'markerfacecolor':'red', 'markersize':6})
    
    # 美化箱型图
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon']
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # 设置标题和标签
    plt.title('股票价格分布箱型图', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('价格 (元)', fontsize=12)
    plt.xlabel('价格类型', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # 添加统计信息
    stats_text = f"数据统计信息:\n"
    stats_text += f"记录数: {len(df)}\n"
    stats_text += f"时间跨度: {df['date'].min()} 到 {df['date'].max()}"
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # 保存或显示图形
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"价格箱型图已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()

def create_volume_boxplot(df, save_path=None):
    """
    绘制交易量相关字段的箱型图
    
    Args:
        df (pandas.DataFrame): 股票数据
        save_path (str): 保存路径
    """
    # 准备数据
    volume_data = df[['volume', 'amount']].copy()
    volume_data.columns = ['成交量', '成交额']
    
    # 对成交额进行单位转换（亿元）
    volume_data['成交额'] = volume_data['成交额'] / 100000000
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 成交量箱型图
    bp1 = ax1.boxplot(volume_data['成交量'], patch_artist=True, notch=True)
    bp1['boxes'][0].set_facecolor('skyblue')
    bp1['boxes'][0].set_alpha(0.7)
    ax1.set_title('成交量分布', fontsize=14, fontweight='bold')
    ax1.set_ylabel('成交量 (股)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # 成交额箱型图
    bp2 = ax2.boxplot(volume_data['成交额'], patch_artist=True, notch=True)
    bp2['boxes'][0].set_facecolor('lightcoral')
    bp2['boxes'][0].set_alpha(0.7)
    ax2.set_title('成交额分布', fontsize=14, fontweight='bold')
    ax2.set_ylabel('成交额 (亿元)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle('交易量相关指标箱型图', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"交易量箱型图已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()

def create_indicator_boxplot(df, save_path=None):
    """
    绘制其他指标的箱型图
    
    Args:
        df (pandas.DataFrame): 股票数据
        save_path (str): 保存路径
    """
    # 选择其他数值指标
    indicator_columns = ['turn', 'pctChg', 'peTTM', 'pbMRQ']
    indicator_names = ['换手率(%)', '涨跌幅(%)', '市盈率', '市净率']
    
    # 准备数据
    indicator_data = df[indicator_columns].copy()
    indicator_data.columns = indicator_names
    
    # 处理异常值和缺失值
    for col in indicator_data.columns:
        # 移除极值（超过99%分位数的数据）
        q99 = indicator_data[col].quantile(0.99)
        indicator_data.loc[indicator_data[col] > q99, col] = q99
    
    plt.figure(figsize=(14, 10))
    
    # 创建子图
    for i, (col, name) in enumerate(zip(indicator_data.columns, indicator_names)):
        plt.subplot(2, 2, i+1)
        
        # 绘制箱型图
        bp = plt.boxplot(indicator_data[col], patch_artist=True, notch=True)
        bp['boxes'][0].set_facecolor(['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon'][i])
        bp['boxes'][0].set_alpha(0.7)
        
        plt.title(f'{name}分布', fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # 添加统计信息
        mean_val = indicator_data[col].mean()
        median_val = indicator_data[col].median()
        std_val = indicator_data[col].std()
        
        stats_text = f'均值: {mean_val:.2f}\n中位数: {median_val:.2f}\n标准差: {std_val:.2f}'
        plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('股票指标分布箱型图', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"指标箱型图已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()

def create_comprehensive_analysis(df, save_dir='./boxplot_results'):
    """
    创建综合分析报告
    
    Args:
        df (pandas.DataFrame): 股票数据
        save_dir (str): 保存目录
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    print("开始生成箱型图分析...")
    
    # 生成各类箱型图
    price_save_path = os.path.join(save_dir, 'price_boxplot.png')
    create_price_boxplot(df, price_save_path)
    
    volume_save_path = os.path.join(save_dir, 'volume_boxplot.png')
    create_volume_boxplot(df, volume_save_path)
    
    indicator_save_path = os.path.join(save_dir, 'indicator_boxplot.png')
    create_indicator_boxplot(df, indicator_save_path)
    
    # 生成数据统计报告
    report_path = os.path.join(save_dir, 'data_statistics.txt')
    generate_statistics_report(df, report_path)
    
    print(f"\n所有分析结果已保存到目录: {save_dir}")

def generate_statistics_report(df, report_path):
    """
    生成数据统计报告
    
    Args:
        df (pandas.DataFrame): 股票数据
        report_path (str): 报告保存路径
    """
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("股票历史数据统计分析报告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"数据概览:\n")
        f.write(f"- 记录总数: {len(df)} 条\n")
        f.write(f"- 时间范围: {df['date'].min()} 到 {df['date'].max()}\n")
        f.write(f"- 股票代码: {df['code'].iloc[0]}\n\n")
        
        # 数值字段统计
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount', 
                          'turn', 'pctChg', 'peTTM', 'pbMRQ']
        column_names = ['开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额',
                       '换手率', '涨跌幅', '市盈率', '市净率']
        
        f.write("各字段统计信息:\n")
        f.write("-" * 30 + "\n")
        
        for col, name in zip(numeric_columns, column_names):
            if col in df.columns:
                series = df[col]
                f.write(f"\n{name} ({col}):\n")
                f.write(f"  均值: {series.mean():.4f}\n")
                f.write(f"  中位数: {series.median():.4f}\n")
                f.write(f"  标准差: {series.std():.4f}\n")
                f.write(f"  最小值: {series.min():.4f}\n")
                f.write(f"  最大值: {series.max():.4f}\n")
                f.write(f"  25%分位数: {series.quantile(0.25):.4f}\n")
                f.write(f"  75%分位数: {series.quantile(0.75):.4f}\n")
    
    print(f"统计报告已保存到: {report_path}")

def main():
    """主函数"""
    # 数据文件路径
    csv_file = './history_k_data.csv'
    
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"错误: 找不到文件 {csv_file}")
        return
    
    # 加载数据
    print("正在加载股票数据...")
    df = load_stock_data(csv_file)
    
    if df is None:
        return
    
    # 显示数据基本信息
    print("\n数据基本信息:")
    print(df.info())
    print("\n前5行数据:")
    print(df.head())
    
    # 创建综合分析
    create_comprehensive_analysis(df)

if __name__ == "__main__":
    main()