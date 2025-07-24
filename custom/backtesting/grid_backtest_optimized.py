#!/usr/bin/env python3
"""
优化版网格交易策略回测脚本
使用重新计算的网格基准价格5.242 HKD
提高资金利用率和交易频率
"""

import pandas as pd
import sys
import os
from datetime import date, datetime, timedelta
# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)

from custom.strategies.Grid_Trading_Realistic import GridTradingRealistic
from engines.backtesting_engine import BacktestingEngine

from engines.data_engine import HKEXInterface

def run_optimized_grid_backtest():
    """运行优化版网格交易策略回测"""
    
    # 更新证券列表
    print("更新证券列表...")
    HKEXInterface.update_security_list_full()
    
    # 设置回测参数
    end_date = date(2025, 7, 23)
    start_date = end_date - timedelta(days=100)
    stock_list = ['HK.03033']  # 南方恒生科技ETF
    
    # 初始化回测引擎
    bt = BacktestingEngine(stock_list=stock_list, start_date=start_date, end_date=end_date, observation=100)
    
    # 准备回测数据
    print("准备回测数据...")
    bt.prepare_input_data_file_1M()  # 使用1分钟数据
    
    # 初始化优化版网格交易策略
    print("初始化优化版网格交易策略...")
    
    # 基于分析结果设置参数
    optimized_base_price = 5.242  # 重新计算的基准价格
    optimized_grid_levels = 15    # 增加网格数量
    optimized_grid_spacing = 0.025  # 减小网格间距至2.5%
    
    strategy = GridTradingRealistic(
        bt.get_backtesting_init_data(), 
        grid_levels=optimized_grid_levels, 
        grid_spacing=optimized_grid_spacing, 
        base_price=optimized_base_price
    )
    
    # 在回测引擎中设置策略
    bt.init_strategy(strategy)
    
    # 运行回测
    print("运行优化版回测...")
    bt.calculate_return()
    
    # 生成HTML报告
    print("生成HTML报告...")
    try:
        bt.create_html_report()
        print("报告已生成到backtesting_report目录")
    except Exception as e:
        print(f"生成HTML报告时出错: {e}")
    
    # 输出优化参数
    print("\n" + "="*50)
    print("优化参数对比")
    print("="*50)
    print(f"原基准价格: 5.64 HKD → 优化后: {optimized_base_price} HKD")
    print(f"原网格数量: 10 → 优化后: {optimized_grid_levels}")
    print(f"原网格间距: 3.0% → 优化后: {optimized_grid_spacing*100}%")
    print("="*50)
    
    return bt

if __name__ == "__main__":
    run_optimized_grid_backtest()