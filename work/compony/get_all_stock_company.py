"""
调用akshare接口获取所有的股票信息
股票信息包括
股票代码 股票名称 公司名称 上市日期 市值 所属板块
"""

import akshare as ak
import pandas as pd
import time
import warnings
import os
from pathlib import Path

warnings.filterwarnings("ignore")

# 版本校验（确保≥1.18.0）
print(f"当前AkShare版本：{ak.__version__}")
assert float(ak.__version__[:4]) >= 1.18, "请安装 akshare>=1.18.0"

# 创建csv目录
csv_dir = "./csv"
Path(csv_dir).mkdir(exist_ok=True)


def get_all_stock_full_info_ak18(use_cache=True):
    """
    AkShare 1.18+ 版本专用：获取所有A股核心信息
    输出字段：股票代码、股票名称、公司名称、上市日期、市值、所属板块
    use_cache: 是否使用缓存文件，默认True
    """
    # -------------------------- 1. 获取全A股基础列表（代码+简称） --------------------------
    code_csv_path = os.path.join(csv_dir, "股票代码+名称.csv")
    
    if use_cache and os.path.exists(code_csv_path):
        print("【1/4】检测到缓存文件，直接读取股票代码+名称...")
        df_code = pd.read_csv(code_csv_path, encoding="utf-8-sig")
        print(f"从缓存读取 {len(df_code)} 只A股")
    else:
        print("【1/4】获取全A股代码+简称...")
        # 1.18+版本返回格式：code带后缀（如600519.SH），需清洗
        df_code = ak.stock_info_a_code_name()
        df_code.rename(columns={
            "code": "股票代码_带后缀",
            "name": "股票名称"
        }, inplace=True)
        # 提取纯6位代码（去掉.SH/.SZ/.BJ后缀）
        df_code["股票代码"] = df_code["股票代码_带后缀"].str.split(".").str[0]
        df_code = df_code[["股票代码", "股票名称"]]
        print(f"共获取 {len(df_code)} 只A股")
        df_code.to_csv(code_csv_path, index=False, encoding="utf-8-sig")
    
    # -------------------------- 2. 获取实时行情：总市值 + 所属板块 --------------------------
    spot_csv_path = os.path.join(csv_dir, "实时市值+所属板块.csv")
    
    if use_cache and os.path.exists(spot_csv_path):
        print("【2/4】检测到缓存文件，直接读取实时市值+所属板块...")
        df_spot = pd.read_csv(spot_csv_path, encoding="utf-8-sig")
    else:
        print("【2/4】获取实时市值+所属板块...")
        # 1.18+版本字段变化：总市值→总市值_元，市场类型→板块
        df_spot = ak.stock_zh_a_spot_em()
        df_spot = df_spot.rename(columns={
            "代码": "股票代码",
            "总市值_元": "总市值(元)",  # 1.18+核心字段变化
            "板块": "所属板块",  # 1.18+字段名调整（原市场类型）
            "行业": "申万一级行业"
        })[["股票代码", "总市值(元)", "所属板块", "申万一级行业"]]
        df_spot.to_csv(spot_csv_path, index=False, encoding="utf-8-sig")
    
    # -------------------------- 3. 批量获取：公司全称 + 上市日期 --------------------------
    info_csv_path = os.path.join(csv_dir, "公司全称+上市日期.csv")
    
    if use_cache and os.path.exists(info_csv_path):
        print("【3/4】检测到缓存文件，直接读取公司全称+上市日期...")
        df_info = pd.read_csv(info_csv_path, encoding="utf-8-sig")
    else:
        print("【3/4】批量获取公司全称+上市日期（约8分钟）...")
        info_list = []
        # 按代码遍历，添加反爬延迟
        for idx, code in enumerate(df_code["股票代码"].tolist()):
            try:
                # 1.18+版本：stock_profile_ths字段调整（上市日期→上市时间）
                df_profile = ak.stock_profile_ths(symbol=code)
                if not df_profile.empty:
                    info = {
                        "股票代码": code,
                        "公司名称": df_profile["公司名称"].iloc[0],  # 公司全称
                        "上市日期": df_profile["上市时间"].iloc[0]  # 1.18+字段名变化
                    }
                    info_list.append(info)
                else:
                    info_list.append({"股票代码": code, "公司名称": "无", "上市日期": "无"})
            except Exception as e:
                # 个别股票接口异常，标注失败不中断
                info_list.append({"股票代码": code, "公司名称": "获取失败", "上市日期": "获取失败"})

            # 反爬延迟（核心：避免IP被封）
            time.sleep(0.5)
            # 进度提示
            if (idx + 1) % 500 == 0:
                print(f"已处理 {idx + 1}/{len(df_code)} 只股票")

        df_info = pd.DataFrame(info_list)
        df_info.to_csv(info_csv_path, index=False, encoding="utf-8-sig")
    
    # -------------------------- 4. 合并数据 + 整理输出 --------------------------
    print("【4/4】合并数据并保存...")
    # 合并所有维度数据
    df_merge = pd.merge(df_code, df_info, on="股票代码", how="left")
    df_merge = pd.merge(df_merge, df_spot, on="股票代码", how="left")

    # 只保留你需要的核心字段
    final_cols = [
        "股票代码", "股票名称", "公司名称",
        "上市日期", "总市值(元)", "所属板块"
    ]
    df_final = df_merge[final_cols]

    # 数据清洗（处理空值/异常值）
    df_final["总市值(元)"] = df_final["总市值(元)"].fillna("0")
    df_final["所属板块"] = df_final["所属板块"].fillna("未知")

    # 保存为CSV（UTF-8编码，Excel打开无乱码）
    save_path = "全A股核心信息_AkShare1.18+.csv"
    df_final.to_csv(save_path, index=False, encoding="utf-8-sig")

    # 输出结果
    print(f"\n✅ 数据获取完成！")
    print(f"📊 共获取 {len(df_final)} 只A股信息")
    print(f"💾 数据已保存至：{save_path}")
    print("\n📈 前5条数据预览：")
    print(df_final.head())

    return df_final


if __name__ == "__main__":
    # 执行主函数，启用缓存
    df_result = get_all_stock_full_info_ak18(use_cache=True)
