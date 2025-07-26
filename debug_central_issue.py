#!/usr/bin/env python
"""
调试中枢识别问题的测试脚本
"""
import pandas as pd
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor
# 从custom目录导入数据获取函数
from custom.chanlun_selector_demo import get_stock_data


def debug_central_issue():
    """调试中枢识别问题"""
    print("=== 调试中枢识别问题 ===")
    
    # 获取数据
    data = get_stock_data("0700.HK", period="2y", interval="1d")
    data = data.tail(50).reset_index(drop=True)
    
    print(f"原始数据长度: {len(data)}")
    
    # 缠论分析
    processor = ChanlunProcessor()
    result = processor.process(data)
    
    # 打印详细信息
    print(f"合并后数据长度: {len(result['merged_df'])}")
    print(f"分型数量: {len(result['fractals'])}")
    print(f"笔数量: {len(result['strokes'])}")
    print(f"中枢数量: {len(result['centrals'])}")
    
    # 打印所有中枢的详细信息
    print("\n中枢详情:")
    for i, central in enumerate(result['centrals']):
        print(f"  中枢 {i+1}: 起始索引={central.start_index}, 结束索引={central.end_index}, ")
        print(f"           高点={central.high:.2f}, 低点={central.low:.2f}")
        
        # 检查中枢的有效性
        if central.high <= central.low:
            print(f"    ❌ 无效中枢: 高点不大于低点")
        
        # 检查索引范围
        if central.start_index < 0 or central.end_index >= len(result['merged_df']):
            print(f"    ❌ 索引越界: start_index={central.start_index}, end_index={central.end_index}")
            
        # 检查构成中枢的三笔
        if i * 3 + 2 < len(result['strokes']):
            stroke1 = result['strokes'][i * 3]
            stroke2 = result['strokes'][i * 3 + 1]
            stroke3 = result['strokes'][i * 3 + 2]
            print(f"    构成笔: {stroke1.direction} -> {stroke2.direction} -> {stroke3.direction}")
    
    # 打印所有笔的信息
    print("\n笔详情:")
    for i, stroke in enumerate(result['strokes']):
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔 {i+1}: {direction_str}, 起始索引={stroke.start_index}, 结束索引={stroke.end_index}")
        print(f"       起始价格={stroke.start_price:.2f}, 结束价格={stroke.end_price:.2f}")


if __name__ == "__main__":
    debug_central_issue()