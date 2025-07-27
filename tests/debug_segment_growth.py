#!/usr/bin/env python3
"""
调试线段生长逻辑
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.segment_builder import SegmentBuilder
from util.chanlun import Stroke


def debug_segment_growth():
    """调试线段生长"""
    print("=== 调试线段生长逻辑 ===")
    
    builder = SegmentBuilder()
    
    # 创建测试数据
    strokes = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=110, direction=1, idx=1),   # 上涨
        Stroke(start_index=5, end_index=10, start_price=110, end_price=105, direction=-1, idx=2), # 下跌
        Stroke(start_index=10, end_index=15, start_price=105, end_price=120, direction=1, idx=3), # 上涨
        Stroke(start_index=15, end_index=20, start_price=120, end_price=115, direction=-1, idx=4), # 下跌
        Stroke(start_index=20, end_index=25, start_price=115, end_price=130, direction=1, idx=5), # 上涨
        Stroke(start_index=25, end_index=30, start_price=130, end_price=125, direction=-1, idx=6), # 下跌
        Stroke(start_index=30, end_index=35, start_price=125, end_price=140, direction=1, idx=7), # 上涨（反向）
    ]
    
    print("笔序列:")
    for i, stroke in enumerate(strokes):
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔{i+1}: {direction_str}, 索引 {stroke.start_index}->{stroke.end_index}")
    
    # 调试生长过程
    start_idx = 0
    segment_direction = strokes[start_idx].direction
    print(f"\n从笔{start_idx+1}开始生长:")
    print(f"线段方向: {'上涨' if segment_direction == 1 else '下跌'}")
    
    # 手动跟踪生长过程
    i = start_idx
    print(f"开始索引: {i}")
    while i < len(strokes) and strokes[i].direction == segment_direction:
        print(f"  检查笔{i+1}: 方向={'上涨' if strokes[i].direction == 1 else '下跌'} - {'匹配' if strokes[i].direction == segment_direction else '不匹配'}")
        i += 1
    
    print(f"结束索引: {i}")
    end_idx = i - 1 if i > start_idx else start_idx
    print(f"线段终点: {end_idx} (笔{end_idx+1})")
    
    # 使用方法测试
    method_end_idx = builder.find_segment_end_by_growth(strokes, start_idx)
    print(f"方法返回终点: {method_end_idx} (笔{method_end_idx+1})")
    
    print("\n=== 调试完成 ===")


def main():
    """主调试函数"""
    debug_segment_growth()


if __name__ == "__main__":
    main()