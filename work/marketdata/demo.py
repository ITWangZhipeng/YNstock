import asyncio
import websockets
import json
import time

# -------------------------- 配置信息（新版核心修改） --------------------------
JQ_TOKEN = "你的QuantApi Token"  # 替换为自己的Token
WS_URL = "wss://push2.joinquant.com/websocket/quote"
SUBSCRIBE_CODES = ["600519.XSHG", "000001.XSHE", "300750.XSHE"]


# -------------------------- WebSocket核心逻辑（移除get_auth_header） --------------------------
async def jqdata_ws_quote():
    """新版JQData WebSocket订阅实时行情（无get_auth_header）"""
    # 1. 建立WebSocket连接
    async with websockets.connect(WS_URL) as websocket:
        print("✅ 已连接JQData WebSocket服务器")

        # 2. 新版认证：直接用QuantApi Token登录（无需调用jqdatasdk.auth）
        auth_params = {
            "method": "login",
            "params": {
                "token": JQ_TOKEN,  # 直接填QuantApi Token
                "user_agent": "jqdata_python/1.0",
                "version": "1.0"
            },
            "id": int(time.time() * 1000)  # 请求ID（唯一）
        }
        await websocket.send(json.dumps(auth_params))

        # 接收认证响应
        auth_resp = await websocket.recv()
        auth_resp_dict = json.loads(auth_resp)
        if auth_resp_dict.get("error") is None:
            print("✅ JQData认证成功")
        else:
            print(f"❌ JQData认证失败：{auth_resp_dict['error']}")
            return

        # 3. 订阅行情（逻辑不变）
        subscribe_params = {
            "method": "subscribe",
            "params": {
                "codes": SUBSCRIBE_CODES,
                "fields": [
                    "last_price", "open_price", "high_price", "low_price",
                    "pre_close", "volume", "amount", "total_market_value",
                    "circulating_market_value", "timestamp"
                ]
            },
            "id": int(time.time() * 1000) + 1
        }
        await websocket.send(json.dumps(subscribe_params))
        print(f"✅ 已订阅股票：{SUBSCRIBE_CODES}")

        # 4. 循环接收行情（逻辑不变）
        print("\n📈 开始接收实时行情（按Ctrl+C停止）：")
        while True:
            try:
                data = await websocket.recv()
                data_dict = json.loads(data)

                # 处理心跳包
                if data_dict.get("method") == "ping":
                    pong_params = {"method": "pong", "id": data_dict["id"]}
                    await websocket.send(json.dumps(pong_params))
                    continue

                # 解析行情数据
                if data_dict.get("params") and data_dict["params"].get("data"):
                    quote_data = data_dict["params"]["data"]
                    for code, fields in quote_data.items():
                        print(f"\n【{code}】")
                        print(f"  最新价：{fields.get('last_price', '-')} 元")
                        print(
                            f"  涨跌幅：{round((fields.get('last_price', 0) - fields.get('pre_close', 0)) / fields.get('pre_close', 1) * 100, 2)} %")
                        print(f"  总市值：{fields.get('total_market_value', '-')} 元")
                        print(f"  成交量：{fields.get('volume', '-')} 手")
                        print(
                            f"  时间戳：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fields.get('timestamp', 0) / 1000))}")

            except websockets.exceptions.ConnectionClosed:
                print("❌ WebSocket连接断开，正在重连...")
                await asyncio.sleep(3)
                await jqdata_ws_quote()
                break
            except KeyboardInterrupt:
                print("\n🛑 用户终止，关闭WebSocket连接")
                break
            except Exception as e:
                print(f"❌ 接收数据异常：{str(e)}")
                continue


if __name__ == "__main__":
    try:
        asyncio.run(jqdata_ws_quote())
    except Exception as e:
        print(f"❌ 程序异常：{str(e)}")