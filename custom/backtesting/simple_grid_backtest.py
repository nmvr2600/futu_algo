import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies.Grid_Trading import GridTrading
from datetime import date, datetime

# 创建一个简化的回测脚本
def run_grid_backtest():
    # 为HK.03033创建回测
    stock_code = 'HK.03033'
    
    # 直接从parquet文件读取数据
    data_file = f'data/{stock_code}/{stock_code}_2025_1D.parquet'
    stock_data = pd.read_parquet(data_file)
    
    # 设置回测时间范围
    start_date = date(2024, 7, 1)
    end_date = date(2025, 7, 23)
    
    # 过滤数据范围
    stock_data['time_key'] = pd.to_datetime(stock_data['time_key'])
    mask = (stock_data['time_key'].dt.date >= start_date) & (stock_data['time_key'].dt.date <= end_date)
    stock_data = stock_data[mask]
    
    # 初始化输入数据
    input_data = {stock_code: stock_data}
    
    # 创建网格策略实例
    strategy = GridTrading(input_data, grid_levels=10, grid_spacing=0.05, base_price=5.64)
    
    # 运行简单的回测
    print("开始网格策略回测...")
    print(f"股票: HK.03033")
    print(f"时间范围: {start_date} 到 {end_date}")
    print(f"基准价格: 5.64")
    print(f"网格间距: 5%")
    
    # 简单的回测逻辑
    buy_signals = 0
    sell_signals = 0
    
    # 获取HK.03033的数据
    stock_data = input_data['HK.03033']
    
    for i in range(10, len(stock_data)):
        # 更新数据
        current_data = stock_data.iloc[:i+1].copy()
        
        # 创建临时策略实例进行测试
        temp_input = {'HK.03033': current_data}
        temp_strategy = GridTrading(temp_input, grid_levels=10, grid_spacing=0.05, base_price=5.64)
        
        # 检查买卖信号
        if temp_strategy.buy('HK.03033'):
            buy_signals += 1
            if buy_signals <= 5:  # 只显示前5个买入信号
                print(f"买入信号: {current_data.iloc[-1]['time_key']} 价格: {current_data.iloc[-1]['close']}")
            
        if temp_strategy.sell('HK.03033'):
            sell_signals += 1
            if sell_signals <= 5:  # 只显示前5个卖出信号
                print(f"卖出信号: {current_data.iloc[-1]['time_key']} 价格: {current_data.iloc[-1]['close']}")
    
    print(f"\n回测结果:")
    print(f"总买入信号数: {buy_signals}")
    print(f"总卖出信号数: {sell_signals}")

if __name__ == "__main__":
    run_grid_backtest()