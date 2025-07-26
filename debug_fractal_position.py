#!/usr/bin/env python
"""
调试分型位置映射问题的测试脚本
"""
import pandas as pd
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor
from chanlun_advanced_visualizer import generate_divergence_chart
# 从custom目录导入数据获取函数
from custom.chanlun_selector_demo import get_stock_data


def debug_fractal_position_mapping():
    """调试分型位置映射问题"""
    print("=== 调试分型位置映射问题 ===")
    
    # 生成0700.HK的图表，使用-k 50参数
    chart_path = generate_divergence_chart(
        "0700.HK", period="2y", interval="1d", kline_count=50, save_dir="./debug_reports"
    )
    print(f"生成的图表路径: {chart_path}")
    
    # 额外的调试信息
    print("\n=== 额外调试信息 ===")
    
    # 获取数据
    data = get_stock_data("0700.HK", period="2y", interval="1d")
    data = data.tail(50).reset_index(drop=True)
    
    # 缠论分析
    processor = ChanlunProcessor()
    result = processor.process(data)
    
    # 打印一些关键信息
    print(f"原始数据长度: {len(data)}")
    print(f"合并后数据长度: {len(result['merged_df'])}")
    print(f"分型数量: {len(result['fractals'])}")
    
    # 打印索引映射信息
    print("\n索引映射信息:")
    if 'index_mapping' in result:
        print(f"  索引映射数量: {len(result['index_mapping'])}")
        # 打印前几个索引映射
        for i, (merged_idx, original_indices) in enumerate(result['index_mapping'].items()):
            if i >= 5:  # 只打印前5个
                break
            print(f"  合并索引 {merged_idx} -> 原始索引 {original_indices}")
    
    # 打印前几个分型的索引信息
    print("\n分型索引详情:")
    for i, fractal in enumerate(result['fractals'][:5]):
        type_str = "顶" if fractal.type.value == "top" else "底"
        print(f"  分型 {fractal.idx}: {type_str}分型，合并索引={fractal.index}")
        
        # 查看对应的原始索引
        if fractal.index < len(result['merged_df']):
            original_indices = result['merged_df'].iloc[fractal.index]['original_indices']
            print(f"    对应的原始索引: {original_indices}")
            
            # 如果有索引映射，也打印映射后的索引
            if 'index_mapping' in result and fractal.index in result['index_mapping']:
                mapped_indices = result['index_mapping'][fractal.index]
                print(f"    映射后的索引: {mapped_indices}")
    
    # 打印笔信息
    print("\n笔信息:")
    for i, stroke in enumerate(result['strokes'][:5]):  # 只打印前5个笔
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔 {stroke.idx}: {direction_str}笔")
        print(f"    起始索引: {stroke.start_index}, 结束索引: {stroke.end_index}")
        print(f"    起始价格: {stroke.start_price:.3f}, 结束价格: {stroke.end_price:.3f}")
        
        # 查看对应的原始索引
        if stroke.start_index < len(result['merged_df']):
            start_original = result['merged_df'].iloc[stroke.start_index]['original_indices']
            print(f"    起始原始索引: {start_original}")
        if stroke.end_index < len(result['merged_df']):
            end_original = result['merged_df'].iloc[stroke.end_index]['original_indices']
            print(f"    结束原始索引: {end_original}")


if __name__ == "__main__":
    debug_fractal_position_mapping()