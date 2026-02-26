import pandas as pd
import requests
import json
import time
import random
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/"
}
# 替换第1步：从东方财富获取A股基础列表（无AkShare）
def get_stock_code_from_eastmoney():
    """
    分页获取东方财富股票数据
    每页100条，共55页
    """
    url = "http://81.push2.eastmoney.com/api/qt/clist/get"
    all_data = []

    print("🚀 开始分页获取股票数据 (每页100条，共55页)")

    # 循环55页，每页100条
    for page in range(1, 56):  # 1到55页
        try:
            params = {
                "pn": page,  # 页码
                "pz": 100,  # 每页条数
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f3",
                "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23",
                "fields": "f12,f14,f20,f107,f102,f62,f3"  # 股票代码、名称、市值等
            }

            print(f"正在获取第 {page}/55 页...")
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "data" in data and "diff" in data["data"]:
                    page_data = data["data"]["diff"]
                    if page_data:
                        all_data.extend(page_data)
                        print(f"  ✓ 第 {page} 页获取到 {len(page_data)} 条记录")
                    else:
                        print(f"  ⚠ 第 {page} 页无数据")
                else:
                    print(f"  ✗ 第 {page} 页数据格式异常")
            else:
                print(f"  ✗ 第 {page} 页请求失败: {response.status_code}")

            # 添加随机延迟避免被封
            time.sleep(random.uniform(3, 6))

        except Exception as e:
            print(f"  ✗ 获取第 {page} 页失败: {str(e)}")
            continue

    # 处理获取到的所有数据
    if all_data:
        print(f"\n📊 总共获取到 {len(all_data)} 条股票数据")
        df = pd.DataFrame(all_data)

        # 重命名列
        column_mapping = {
            "f12": "股票代码",
            "f14": "股票名称",
            "f20": "总市值",
            "f107": "所属板块",
            "f102": "申万一级行业",
            "f62": "主力净流入",
            "f3": "最新价"
        }

        # 只保留存在的列
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df.rename(columns=existing_columns, inplace=True)

        # 选择需要的列
        needed_columns = [v for v in existing_columns.values()]
        result_df = df[needed_columns].copy()

        print(f"✅ 数据处理完成，共 {len(result_df)} 条有效记录")
        return result_df
    else:
        print("❌ 未获取到任何数据")
        return pd.DataFrame()

# 替换第3步：从东方财富获取公司全称+上市日期
def get_company_info_from_eastmoney(code):
    url = f"http://push2.eastmoney.com/api/qt/stock/get?secid=0.{code}" if code.startswith(("6","9")) else f"http://push2.eastmoney.com/api/qt/stock/get?secid=1.{code}"
    params = {"fields":"f102,f104,f124,f100"}  # f100=公司全称, f104=上市日期
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()["data"]
    return {
        "股票代码": code,
        "公司名称": data.get("f100", "未知"),
        "上市日期": data.get("f104", "未知")
    }