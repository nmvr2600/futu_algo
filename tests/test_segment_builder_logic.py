#!/usr/bin/env python3
"""
测试线段构建逻辑
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.segment_builder import SegmentBuilder
from util.chanlun import Stroke


def test_segment_start_detection():
    """测试线段起点检测"""
    print("=== 测试线段起点检测 ===")
    
    builder = SegmentBuilder()
    
    # 创建满足条件的前三笔：下跌->上涨->下跌
    valid_strokes = [
        Stroke(start_index=0, end_index=5, start_price=120, end_price=100, direction=-1, idx=1),  # 下跌
        Stroke(start_index=5, end_index=10, start_price=100, end_price=130, direction=1, idx=2),   # 上涨
        Stroke(start_index=10, end_index=15, start_price=130, end_price=110, direction=-1, idx=3), # 下跌
    ]
    
    # 价格区间有重叠，应该能形成线段起点
    can_form = builder.can_form_segment_start(valid_strokes, 0)
    print(f"有效前三笔检测: {'可以形成' if can_form else '不能形成'}")
    
    # 创建不满足条件的前三笔：下跌->上涨->上涨
    invalid_strokes = [
        Stroke(start_index=0, end_index=5, start_price=120, end_price=100, direction=-1, idx=1),  # 下跌
        Stroke(start_index=5, end_index=10, start_price=100, end_price=130, direction=1, idx=2),   # 上涨
        Stroke(start_index=10, end_index=15, start_price=130, end_price=150, direction=1, idx=3),  # 上涨（同向）
    ]
    
    # 方向不交替，不能形成线段起点
    can_form = builder.can_form_segment_start(invalid_strokes, 0)
    print(f"无效前三笔检测: {'可以形成' if can_form else '不能形成'}")
    
    print("✅ 线段起点检测测试完成\n")


def test_segment_growth():
    """测试线段生长"""
    print("=== 测试线段生长 ===")
    
    builder = SegmentBuilder()
    
    # 创建同向笔序列
    strokes = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=110, direction=1, idx=1),   # 上涨
        Stroke(start_index=5, end_index=10, start_price=110, end_price=105, direction=-1, idx=2), # 下跌
        Stroke(start_index=10, end_index=15, start_price=105, end_price=120, direction=1, idx=3), # 上涨
        Stroke(start_index=15, end_index=20, start_price=120, end_price=115, direction=-1, idx=4), # 下跌
        Stroke(start_index=20, end_index=25, start_price=115, end_price=130, direction=1, idx=5), # 上涨
        Stroke(start_index=25, end_index=30, start_price=130, end_price=125, direction=-1, idx=6), # 下跌
        Stroke(start_index=30, end_index=35, start_price=125, end_price=140, direction=1, idx=7), # 上涨（反向）
    ]
    
    # 从索引0开始生长，应该找到所有上涨笔
    end_idx = builder.find_segment_end_by_growth(strokes, 0)
    print(f"线段生长终点: {end_idx} (笔{strokes[end_idx].idx})")
    
    # 验证是否包含了所有上涨笔
    expected_end = 4  # 应该是笔5（索引4）
    print(f"期望终点: {expected_end}")
    print(f"生长结果: {'正确' if end_idx == expected_end else '错误'}")
    
    print("✅ 线段生长测试完成\n")


def test_complete_segment_building():
    """测试完整线段构建"""
    print("=== 测试完整线段构建 ===")
    
    builder = SegmentBuilder()
    
    # 创建明确的多线段走势
    strokes = [
        # 第一个上涨线段
        Stroke(start_index=0, end_index=5, start_price=100, end_price=110, direction=1, idx=1, fractal_start=1, fractal_end=2),
        Stroke(start_index=5, end_index=8, start_price=110, end_price=105, direction=-1, idx=2, fractal_start=2, fractal_end=3),
        Stroke(start_index=8, end_index=12, start_price=105, end_price=120, direction=1, idx=3, fractal_start=3, fractal_end=4),
        Stroke(start_index=12, end_index=15, start_price=120, end_price=115, direction=-1, idx=4, fractal_start=4, fractal_end=5),
        Stroke(start_index=15, end_index=20, start_price=115, end_price=130, direction=1, idx=5, fractal_start=5, fractal_end=6),
        
        # 破坏性下跌
        Stroke(start_index=20, end_index=30, start_price=130, end_price=80, direction=-1, idx=6, fractal_start=6, fractal_end=7),
        
        # 第二个下跌线段
        Stroke(start_index=30, end_index=35, start_price=80, end_price=90, direction=1, idx=7, fractal_start=7, fractal_end=8),
        Stroke(start_index=35, end_index=40, start_price=90, end_price=70, direction=-1, idx=8, fractal_start=8, fractal_end=9),
        Stroke(start_index=40, end_index=45, start_price=70, end_price=75, direction=1, idx=9, fractal_start=9, fractal_end=10),
        Stroke(start_index=45, end_index=50, start_price=75, end_price=60, direction=-1, idx=10, fractal_start=10, fractal_end=11),
    ]
    
    segments = builder.build_segments(strokes)
    
    print(f"输入笔数量: {len(strokes)}")
    print(f"生成线段数量: {len(segments)}")
    
    for i, segment in enumerate(segments):
        direction_str = "上涨" if segment.direction == 1 else "下跌"
        print(f"  线段{segment.idx}: {direction_str}, 索引 {segment.start_index}->{segment.end_index}")
    
    # 验证应该生成多个线段
    if len(segments) >= 2:
        print("✅ 生成了多个线段")
        
        # 验证方向交替性
        direction_alternating = True
        for i in range(1, len(segments)):
            if segments[i-1].direction == segments[i].direction:
                direction_alternating = False
                break
        
        if direction_alternating:
            print("✅ 线段方向正确交替")
        else:
            print("❌ 线段方向未交替")
    else:
        print("❌ 未生成多个线段")
    
    print("✅ 完整线段构建测试完成\n")


def main():
    """主测试函数"""
    print("🚀 开始线段构建逻辑测试...\n")
    
    test_segment_start_detection()
    test_segment_growth()
    test_complete_segment_building()
    
    print("🎉 线段构建逻辑测试完成！")


if __name__ == "__main__":
    main()