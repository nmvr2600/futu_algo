#!/usr/bin/env python
"""
测试中枢识别逻辑
"""
import pandas as pd
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Stroke


def test_central_logic():
    """测试中枢识别逻辑"""
    print("=== 测试中枢识别逻辑 ===")
    
    # 创建测试数据 - 模拟一个简单的中枢模式
    # 笔1: 下跌 524.50 -> 489.60
    # 笔2: 上涨 489.60 -> 521.00
    # 笔3: 下跌 521.00 -> 504.50
    
    # 模拟从调试输出中获取的前3笔数据
    stroke1 = Stroke(
        start_index=2,
        end_index=8,
        start_price=524.50,
        end_price=489.60,
        direction=-1  # 下跌
    )
    
    stroke2 = Stroke(
        start_index=8,
        end_index=12,
        start_price=489.60,
        end_price=521.00,
        direction=1   # 上涨
    )
    
    stroke3 = Stroke(
        start_index=12,
        end_index=15,
        start_price=521.00,
        end_price=504.50,
        direction=-1  # 下跌
    )
    
    print(f"笔1: 方向={stroke1.direction}, 起始价格={stroke1.start_price}, 结束价格={stroke1.end_price}")
    print(f"笔2: 方向={stroke2.direction}, 起始价格={stroke2.start_price}, 结束价格={stroke2.end_price}")
    print(f"笔3: 方向={stroke3.direction}, 起始价格={stroke3.start_price}, 结束价格={stroke3.end_price}")
    
    # 检查是否满足中枢形成条件
    print("\n检查中枢形成条件:")
    print(f"1. 笔1和笔3方向相同: {stroke1.direction == stroke3.direction}")
    print(f"2. 笔2方向与前两笔相反: {stroke1.direction != stroke2.direction and stroke2.direction != stroke3.direction}")
    
    if stroke1.direction == stroke3.direction and stroke1.direction != stroke2.direction:
        print("\n计算重叠区间:")
        if stroke1.direction == 1:  # 向上笔
            # 重叠区间为：[max(第1笔起点, 第3笔终点), min(第1笔终点, 第3笔起点)]
            overlap_high = min(stroke1.end_price, stroke3.start_price)
            overlap_low = max(stroke1.start_price, stroke3.end_price)
        else:  # 向下笔
            # 重叠区间为：[max(第1笔终点, 第3笔起点), min(第1笔起点, 第3笔终点)]
            overlap_high = min(stroke1.start_price, stroke3.end_price)
            overlap_low = max(stroke1.end_price, stroke3.start_price)
        
        print(f"重叠区间: {overlap_low} - {overlap_high}")
        
        # 检查第2笔是否在重叠区间内
        if stroke2.direction == 1:  # 向上笔
            second_range_high = stroke2.end_price
            second_range_low = stroke2.start_price
        else:  # 向下笔
            second_range_high = stroke2.start_price
            second_range_low = stroke2.end_price
        
        print(f"第2笔区间: {second_range_low} - {second_range_high}")
        
        # 判断第2笔是否与重叠区间有交集
        has_overlap = max(overlap_low, second_range_low) <= min(overlap_high, second_range_high)
        print(f"第2笔是否在重叠区间内: {has_overlap}")
        
        if has_overlap:
            print("\n✅ 应该形成中枢!")
        else:
            print("\n❌ 不形成中枢")
            print(f"重叠区间的高点和低点: {overlap_high}, {overlap_low}")
            print(f"第2笔区间的高点和低点: {second_range_high}, {second_range_low}")
            print(f"实际比较: max({overlap_low}, {second_range_low}) <= min({overlap_high}, {second_range_high})")
            print(f"即: {max(overlap_low, second_range_low)} <= {min(overlap_high, second_range_high)}")
    else:
        print("\n❌ 不满足中枢形成的基本条件")

if __name__ == "__main__":
    test_central_logic()