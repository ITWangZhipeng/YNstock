from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
from typing import Optional

app = FastAPI()


@app.get("/get/k")
async def root():
    return {"message": "Hello World"}

@app.get("/api/stock-data/{filename}")
async def get_stock_data(filename: str):
    """
    获取股票CSV数据
    
    Args:
        filename (str): 文件名，例如: history_k_data
    
    Returns:
        dict: 包含CSV数据的JSON响应
    """
    try:
        # 构建文件路径
        file_path = f"./work/stock/{filename}.csv"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"文件 {filename}.csv 不存在")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 转换为字典格式返回
        data = df.to_dict(orient='records')
        
        return {
            "filename": filename,
            "total_records": len(data),
            "columns": list(df.columns),
            "data": data
        }
        
    except HTTPException:
        # 重新抛出已有的HTTP异常
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="文件未找到")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/api/stock-files")
async def list_stock_files():
    """
    列出所有可用的股票数据文件
    
    Returns:
        dict: 文件列表
    """
    try:
        stock_dir = "./work/stock"
        if not os.path.exists(stock_dir):
            return {"files": []}
        
        # 查找所有CSV文件
        csv_files = [f[:-4] for f in os.listdir(stock_dir) if f.endswith('.csv')]
        
        return {
            "files": csv_files,
            "count": len(csv_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == '__main__':
    import uvicorn
    import sys
    
    # 解析命令行参数
    port = 8000
    if '--port' in sys.argv:
        try:
            port_index = sys.argv.index('--port') + 1
            if port_index < len(sys.argv):
                port = int(sys.argv[port_index])
        except (ValueError, IndexError):
            print("端口参数无效，使用默认端口8000")
    
    print(f"启动服务器，端口: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)