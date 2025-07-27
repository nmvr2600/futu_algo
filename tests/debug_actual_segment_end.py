#!/usr/bin/env python3
"""
调试实际线段终点查找
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.segment_builder import SegmentBuilder
from util.chanlun import Stroke


def debug_actual_segment_end():
    """调试实际线段终点查找"""
    print("=== 调试实际线段终点查找 ===")
    
    builder = SegmentBuilder()
    
    # 使用之前的测试数据
    strokes = [
        Stroke(start_index=0, end_index=5, start_price=120, end_price=100, direction=-1, idx=1),  # 下跌
        Stroke(start_index=5, end_index=10, start_price=100, end_price=130, direction=1, idx=2),   # 上涨
        Stroke(start_index=10, end_index=15, start_price=130, end_price=110, direction=-1, idx=3), # 下跌
        Stroke(start_index=15, end_index=20, start_price=110, end_price=125, direction=1, idx=4),  # 上涨
        Stroke(start_index=20, end_index=25, start_price=125, end_price=120, direction=-1, idx=5), # 下跌
        Stroke(start_index=25, end_index=30, start_price=120, end_price=135, direction=1, idx=6),  # 上涨
    ]
    
    print("输入笔序列:")
    for i, stroke in enumerate(strokes):
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔{i+1}: {direction_str}, 价格 {stroke.start_price}->{stroke.end_price}")
    
    # 测试起点0的线段终点查找
    start_idx = 0
    print(f"\n测试起点 {start_idx} 的线段终点查找:")
    
    # 检查是否能形成线段起点
    can_form = builder.can_form_segment_start(strokes, start_idx)
    print(f"能否形成线段起点: {'可以' if can_form else '不可以'}")
    
    if can_form:
        # 手动计算应该的终点
        segment_direction = strokes[start_idx].direction
        print(f"线段方向: {'上涨' if segment_direction == 1 else '下跌'}")
        
        # 查找所有同向笔
        i = start_idx
        while i < len(strokes) and strokes[i].direction == segment_direction:
            print(f"  笔{i+1}: 方向={'上涨' if strokes[i].direction == 1 else '下跌'} - {'匹配' if strokes[i].direction == segment_direction else '不匹配'}")
            i += 1
        
        expected_end = i - 1 if i > start_idx else start_idx
        print(f"预期终点: {expected_end} (笔{expected_end+1})")
        
        # 使用方法测试
        actual_end = builder._find_actual_segment_end(strokes, start_idx)
        print(f"实际终点: {actual_end} (笔{actual_end+1})")
        
        print(f"结果: {'正确' if actual_end == expected_end else '错误'}")
    
    print("\n=== 调试完成 ===")


def main():
    """主调试函数"""
    debug_actual_segment_end()


if __name__ == "__main__":
    main()