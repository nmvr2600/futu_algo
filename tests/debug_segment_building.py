#!/usr/bin/env python3
"""
调试线段构建过程
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.segment_builder import SegmentBuilder
from util.chanlun import Stroke


def debug_segment_building():
    """调试线段构建过程"""
    print("=== 调试线段构建过程 ===")
    
    builder = SegmentBuilder()
    
    # 创建明确的测试数据
    strokes = [
        # 明确的下跌->上涨->下跌模式（应该能形成上涨线段）
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
        print(f"  笔{i+1}: {direction_str}, 价格 {stroke.start_price}->{stroke.end_price}, 索引 {stroke.start_index}->{stroke.end_index}")
    
    print(f"\n笔数量: {len(strokes)}")
    
    # 详细检查每个可能的起点
    print("\n检查所有可能的线段起点:")
    for i in range(len(strokes) - 2):
        stroke1 = strokes[i]
        stroke2 = strokes[i + 1]
        stroke3 = strokes[i + 2]
        
        print(f"\n检查起点 {i} (笔{i+1}, {i+2}, {i+3}):")
        direction1_str = "上涨" if stroke1.direction == 1 else "下跌"
        direction2_str = "上涨" if stroke2.direction == 1 else "下跌"
        direction3_str = "上涨" if stroke3.direction == 1 else "下跌"
        print(f"  笔{i+1}: {direction1_str} {stroke1.start_price}->{stroke1.end_price}")
        print(f"  笔{i+2}: {direction2_str} {stroke2.start_price}->{stroke2.end_price}")
        print(f"  笔{i+3}: {direction3_str} {stroke3.start_price}->{stroke3.end_price}")
        
        # 检查方向交替性
        direction_pattern = f"{direction1_str[0]}->{direction2_str[0]}->{direction3_str[0]}"
        print(f"  方向模式: {direction_pattern}")
        
        direction_ok = (stroke1.direction == stroke3.direction and 
                       stroke1.direction != stroke2.direction)
        print(f"  方向交替性: {'✅ 满足' if direction_ok else '❌ 不满足'}")
        
        if direction_ok:
            # 计算价格区间
            if stroke1.direction == 1:  # 向上笔
                range1 = (stroke1.start_price, stroke1.end_price)
                range2 = (stroke2.end_price, stroke2.start_price)  # 下跌笔，区间反转
                range3 = (stroke3.start_price, stroke3.end_price)
            else:  # 向下笔
                range1 = (stroke1.end_price, stroke1.start_price)
                range2 = (stroke2.start_price, stroke2.end_price)
                range3 = (stroke3.end_price, stroke3.start_price)
            
            print(f"  价格区间: range1={range1}, range2={range2}, range3={range3}")
            
            # 计算重叠区间
            overlap_low = max(min(range1), min(range2), min(range3))
            overlap_high = min(max(range1), max(range2), max(range3))
            has_overlap = overlap_low <= overlap_high
            
            print(f"  重叠区间: [{overlap_low:.2f}, {overlap_high:.2f}] - "
                  f"{'✅ 有重叠' if has_overlap else '❌ 无重叠'}")
            
            if has_overlap:
                print(f"  ✅ 起点 {i} 满足条件！")
            else:
                print(f"  ❌ 起点 {i} 不满足重叠条件")
        else:
            print(f"  ❌ 起点 {i} 不满足方向交替条件")
    
    # 使用构建器测试
    print("\n使用构建器测试:")
    segments = builder.build_segments(strokes)
    print(f"生成线段数量: {len(segments)}")
    
    for i, segment in enumerate(segments):
        direction_str = "上涨" if segment.direction == 1 else "下跌"
        print(f"  线段{segment.idx}: {direction_str}, 价格 {segment.start_price:.2f}->{segment.end_price:.2f}, 索引 {segment.start_index}->{segment.end_index}")
    
    print("\n=== 调试完成 ===")


def main():
    """主调试函数"""
    debug_segment_building()


if __name__ == "__main__":
    main()