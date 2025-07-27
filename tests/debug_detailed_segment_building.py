#!/usr/bin/env python3
"""
详细调试线段构建过程
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.segment_builder import SegmentBuilder
from util.chanlun import Stroke


def debug_detailed_segment_building():
    """详细调试线段构建过程"""
    print("=== 详细调试线段构建过程 ===")
    
    # 创建一个新的构建器，启用调试输出
    builder = SegmentBuilder()
    
    # 创建测试数据
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
    
    print(f"\n开始构建线段...")
    segments = []
    
    if len(strokes) < 3:
        print("笔数量不足3笔，无法构建线段")
        return segments
    
    # 手动执行构建算法
    i = 0
    segment_count = 0
    
    while i <= len(strokes) - 3:
        print(f"\n--- 检查起点 {i} ---")
        
        # 检查是否能形成线段起点
        can_form = builder.can_form_segment_start(strokes, i)
        print(f"能否形成线段起点: {'可以' if can_form else '不可以'}")
        
        if not can_form:
            print(f"起点 {i} 不能形成线段，继续检查下一个起点")
            i += 1
            continue
        
        # 找到线段的实际终点
        print(f"查找起点 {i} 的线段终点...")
        segment_end = builder._find_actual_segment_end(strokes, i)
        print(f"线段终点: {segment_end}")
        
        # 检查是否至少包含3笔
        if segment_end >= i + 2:
            print(f"线段包含足够笔数 ({segment_end - i + 1} 笔)")
            
            # 创建线段
            start_stroke = strokes[i]
            end_stroke = strokes[segment_end]
            
            segment_count += 1
            print(f"创建线段 {segment_count}: 从笔{i+1}到笔{segment_end+1}")
            
            segment = Stroke(
                start_index=start_stroke.start_index,
                end_index=end_stroke.end_index,
                start_price=start_stroke.start_price,
                end_price=end_stroke.end_price,
                direction=start_stroke.direction,
                idx=segment_count,
                fractal_start=start_stroke.fractal_start,
                fractal_end=end_stroke.fractal_end
            )
            segments.append(segment)
            
            # 移动到线段结束后的位置继续查找
            print(f"移动到位置 {segment_end + 1}")
            i = segment_end + 1
        else:
            print(f"线段笔数不足 ({segment_end - i + 1} 笔 < 3 笔)")
            i += 1
    
    print(f"\n=== 构建完成 ===")
    print(f"生成线段数量: {len(segments)}")
    
    for i, segment in enumerate(segments):
        direction_str = "上涨" if segment.direction == 1 else "下跌"
        print(f"  线段{segment.idx}: {direction_str}, 价格 {segment.start_price:.2f}->{segment.end_price:.2f}")
    
    # 如果没有生成线段，使用简化处理
    if not segments and len(strokes) >= 3:
        print("\n使用简化处理...")
        # 将连续同向笔合并为线段
        i = 0
        while i < len(strokes):
            current_direction = strokes[i].direction
            j = i
            # 找到连续同向笔
            while j < len(strokes) and strokes[j].direction == current_direction:
                j += 1
            
            if j > i:
                # 创建线段
                start_stroke = strokes[i]
                end_stroke = strokes[j-1]
                
                segment_count += 1
                segment = Stroke(
                    start_index=start_stroke.start_index,
                    end_index=end_stroke.end_index,
                    start_price=start_stroke.start_price,
                    end_price=end_stroke.end_price,
                    direction=current_direction,
                    idx=segment_count,
                    fractal_start=start_stroke.fractal_start,
                    fractal_end=end_stroke.fractal_end
                )
                segments.append(segment)
                print(f"创建线段 {segment_count}: 方向{'上涨' if current_direction == 1 else '下跌'}")
            
            i = j
    
    print(f"\n最终线段数量: {len(segments)}")
    return segments


def main():
    """主调试函数"""
    debug_detailed_segment_building()


if __name__ == "__main__":
    main()