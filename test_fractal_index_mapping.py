"""
测试分形索引映射的正确性
"""
import pandas as pd
import numpy as np
from util.chanlun import ChanlunProcessor


def test_fractal_index_mapping():
    # 创建测试数据
    test_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=10),
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    })
    
    # 添加一些明显的分形模式
    test_data.loc[2, 'high'] = 108  # 顶分形中间点
    test_data.loc[1, 'high'] = 104  # 顶分形左边
    test_data.loc[3, 'high'] = 105  # 顶分形右边
    
    test_data.loc[6, 'low'] = 100   # 底分形中间点
    test_data.loc[5, 'low'] = 103   # 底分形左边
    test_data.loc[7, 'low'] = 104   # 底分形右边
    
    print("原始数据:")
    print(test_data)
    
    # 处理数据
    processor = ChanlunProcessor()
    merged_df, index_mapping, merged_index_map = processor.merge_klines(test_data)
    
    print("\n合并后数据:")
    print(merged_df)
    
    print("\n索引映射关系:")
    print("原始索引 -> 合并索引:", index_mapping)
    print("合并索引 -> 原始索引:", merged_index_map)
    
    # 计算分形
    fractals = processor.calculate_fractals(merged_df)
    print("\n检测到的分形:")
    print(fractals)
    
    # 验证分形位置映射
    if len(fractals) > 0:
        print("\n分形位置验证:")
        for i, fractal in fractals.iterrows():
            merged_index = fractal.name
            if merged_index in merged_index_map:
                original_index = merged_index_map[merged_index]
                print(f"合并索引 {merged_index} -> 原始索引 {original_index}")
                
                # 验证价格是否匹配
                if fractal['fractal_type'] == 'top':
                    expected_price = test_data.loc[original_index, 'high']
                    actual_price = fractal['fractal_value']
                    print(f"  顶分形价格验证: 期望 {expected_price}, 实际 {actual_price}, 匹配: {expected_price == actual_price}")
                else:
                    expected_price = test_data.loc[original_index, 'low']
                    actual_price = fractal['fractal_value']
                    print(f"  底分形价格验证: 期望 {expected_price}, 实际 {actual_price}, 匹配: {expected_price == actual_price}")
    
    return test_data, merged_df, index_mapping, merged_index_map, fractals


def test_visualization_mapping():
    """测试可视化中的索引映射"""
    print("\n=== 可视化索引映射测试 ===")
    
    # 使用真实数据测试
    from custom.chanlun_selector_demo import get_stock_data
    df = get_stock_data('0700.HK', period='50d')
    
    processor = ChanlunProcessor()
    merged_df, index_mapping, merged_index_map = processor.merge_klines(df)
    
    print(f"原始数据长度: {len(df)}")
    print(f"合并数据长度: {len(merged_df)}")
    
    # 计算分形
    fractals = processor.calculate_fractals(merged_df)
    print(f"检测到分形数量: {len(fractals)}")
    
    # 模拟可视化中的索引转换过程
    print("\n可视化索引转换过程:")
    for i, fractal in fractals.head().iterrows():
        merged_index = fractal.name
        print(f"\n分形在合并数据中的索引: {merged_index}")
        
        # 步骤1: 使用merged_index_map获取原始索引
        if merged_index in merged_index_map:
            original_index = merged_index_map[merged_index]
            print(f"  步骤1 - merged_index_map转换: {merged_index} -> {original_index}")
            
            # 步骤2: 使用index_map获取绘图位置
            if original_index in index_mapping:
                plot_position = index_mapping[original_index]
                print(f"  步骤2 - index_map转换: {original_index} -> {plot_position}")
                
                # 验证绘图位置是否在合理范围内
                if 0 <= plot_position < len(merged_df):
                    print(f"  绘图位置验证: {plot_position} 在有效范围内 [0, {len(merged_df)-1}]")
                else:
                    print(f"  绘图位置验证: {plot_position} 超出范围 [0, {len(merged_df)-1}]")
            else:
                print(f"  错误: 原始索引 {original_index} 不在index_mapping中")
        else:
            print(f"  错误: 合并索引 {merged_index} 不在merged_index_map中")


if __name__ == "__main__":
    test_fractal_index_mapping()
    test_visualization_mapping()