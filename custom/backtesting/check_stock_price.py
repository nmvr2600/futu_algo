import pandas as pd
import os
from datetime import datetime

def read_stock_data(stock_code):
    """
    读取指定股票的最新日线数据
    """
    # 构建文件路径
    file_path = f'/Users/macyou/workspace-xhs/futu_algo/data/{stock_code}/{stock_code}_2025_1D.parquet'
    
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取parquet文件
        df = pd.read_parquet(file_path)
        
        # 显示数据的前几行
        print("数据前几行:")
        print(df.head())
        
        # 显示数据的基本信息
        print("\n数据基本信息:")
        print(df.info())
        
        # 显示收盘价的统计信息
        print("\n收盘价统计信息:")
        print(df['close'].describe())
        
        # 显示最近几天的数据
        print("\n最近几天的数据:")
        print(df.tail())
        
        # 获取最新的收盘价作为网格策略的基准价格
        latest_close = df['close'].iloc[-1]
        print(f"\n最新收盘价: {latest_close}")
        
        # 计算一些可能用于网格策略的价格参考值
        mean_price = df['close'].mean()
        median_price = df['close'].median()
        min_price = df['close'].min()
        max_price = df['close'].max()
        
        print(f"\n价格参考信息:")
        print(f"平均价格: {mean_price:.3f}")
        print(f"中位数价格: {median_price:.3f}")
        print(f"最低价格: {min_price:.3f}")
        print(f"最高价格: {max_price:.3f}")
        print(f"价格波动范围: {max_price - min_price:.3f}")
        
        return df
    else:
        print(f"文件不存在: {file_path}")
        return None

if __name__ == "__main__":
    # 读取03033股票数据
    stock_code = "HK.03033"
    df = read_stock_data(stock_code)