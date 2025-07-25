#!/usr/bin/env python3
"""
支持指定K线数量的线段测试脚本
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom.chanlun_selector_demo import get_stock_data
from util.chanlun import ChanlunProcessor
from chanlun_advanced_visualizer import AdvancedChanlunVisualizer


def test_with_kline_count(stock_code="0700.HK", kline_count=60, save_dir="./test_kline_segments"):
    """使用指定数量的K线进行测试"""
    
    print(f"=== 使用{kline_count}根K线测试线段 ===")
    
    try:
        # 获取足够的数据以确保至少有kline_count根
        data = get_stock_data(stock_code, period="2y", interval="1d")
        
        # 限制K线数量
        data = data.tail(kline_count).reset_index(drop=True)
        
        print(f"实际使用K线数量: {len(data)}")
        
        # 缠论分析
        processor = ChanlunProcessor()
        result = processor.process(data)
        
        # 检查结果
        print(f"提取到笔: {len(processor.strokes)}")
        print(f"提取到线段: {len(processor.segments)}")
        
        # 显示所有线段
        if processor.segments:
            print(f"\n所有线段:")
            for i, segment in enumerate(processor.segments):
                direction_str = "向上" if segment.direction == 1 else "向下"
                print(f"  {i}: {direction_str}, "
                      f"起点[{segment.start_index}]{segment.start_price:.2f} -> "
                      f"终点[{segment.end_index}]{segment.end_price:.2f}")
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存有指定K线数量的图表
        output_path = os.path.join(save_dir, f"{stock_code}_kline_{kline_count}.png")
        
        # 创建结果字典
        full_result = {
            "merged_df": processor.merged_df if processor.merged_df is not None else data,
            "fractals": processor.fractals,
            "strokes": processor.strokes,
            "segments": processor.segments,
            "centrals": processor.centrals,
        }
        
        # 创建可视化器
        visualizer = AdvancedChanlunVisualizer()
        visualizer.create_comprehensive_chart(data, full_result, stock_code, output_path)
        
        print(f"\n图表已保存到: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def batch_test_different_counts(stock_code="0700.HK", test_counts=None):
    """批量测试不同数量的K线"""
    if test_counts is None:
        test_counts = [30, 60, 90, 120, 180, 240]
    
    print(f"=== 批量测试 {stock_code} 不同K线数量 ===")
    results = []
    
    for count in test_counts:
        print(f"\n--- 测试 {count} 根K线 ---")
        result = test_with_kline_count(stock_code, count)
        if result:
            results.append((count, result))
    
    print(f"\n=== 批量测试完成 ===")
    for count, path in results:
        print(f"K线数量 {count}: {os.path.basename(path)}")
    
    return results


if __name__ == "__main__":
    # 直接运行测试
    if len(sys.argv) > 1:
        kline_count = int(sys.argv[1])
        test_with_kline_count(kline_count=kline_count)
    else:
        # 批量测试不同K线数量
        batch_test_different_counts()