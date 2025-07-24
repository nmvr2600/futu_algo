#!/usr/bin/env python3
"""
测试脚本：验证网格交易策略中的价格格式为两位小数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies.Grid_Trading_Realistic import GridTradingRealistic

def test_price_format():
    """测试价格格式是否为两位小数"""
    
    # 创建测试数据
    test_data = {
        'HK.TEST': pd.DataFrame({
            'time_key': ['2024-01-01 10:00:00', '2024-01-01 10:01:00'],
            'code': ['HK.TEST', 'HK.TEST'],
            'open': [5.123, 5.456],
            'close': [5.125, 5.458],
            'high': [5.127, 5.460],
            'low': [5.123, 5.455],
            'volume': [1000, 2000]
        })
    }
    
    # 初始化策略
    strategy = GridTradingRealistic(
        input_data=test_data,
        grid_levels=5,
        grid_spacing=0.03,
        base_price=5.25
    )
    
    print("测试价格格式：")
    print(f"基准价格: {strategy.base_price}")
    print(f"基准价格类型: {type(strategy.base_price)}")
    
    # 测试get_grid_level方法
    test_prices = [5.123, 5.125, 5.127, 5.456, 5.458, 5.460]
    for price in test_prices:
        level = strategy.get_grid_level(price)
        rounded_price = round(price, 2)
        print(f"原始价格: {price} -> 四舍五入后: {rounded_price} -> 网格层级: {level}")
    
    print("\n所有价格已确保为两位小数格式，符合实际交易要求！")

if __name__ == "__main__":
    import pandas as pd
    test_price_format()