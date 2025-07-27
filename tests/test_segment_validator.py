#!/usr/bin/env python3
"""
测试线段验证器
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.segment_validator import SegmentValidator
from util.chanlun import Stroke


def test_stroke_continuity_validation():
    """测试笔连续性验证"""
    print("=== 测试笔连续性验证 ===")
    
    # 创建连续的笔
    continuous_strokes = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=110, direction=1, idx=1),
        Stroke(start_index=5, end_index=10, start_price=110, end_price=100, direction=-1, idx=2),
        Stroke(start_index=10, end_index=15, start_price=100, end_price=120, direction=1, idx=3),
    ]
    
    is_valid, errors = SegmentValidator.validate_stroke_continuity(continuous_strokes)
    print(f"连续笔验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    # 创建不连续的笔
    discontinuous_strokes = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=110, direction=1, idx=1),
        Stroke(start_index=6, end_index=10, start_price=110, end_price=100, direction=-1, idx=2),  # 不连续
        Stroke(start_index=10, end_index=15, start_price=100, end_price=120, direction=1, idx=3),
    ]
    
    is_valid, errors = SegmentValidator.validate_stroke_continuity(discontinuous_strokes)
    print(f"不连续笔验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    print("✅ 笔连续性验证测试完成\n")


def test_segment_continuity_validation():
    """测试线段连续性验证"""
    print("=== 测试线段连续性验证 ===")
    
    # 创建连续的线段
    continuous_segments = [
        Stroke(start_index=0, end_index=20, start_price=100, end_price=120, direction=1, idx=1),
        Stroke(start_index=20, end_index=40, start_price=120, end_price=80, direction=-1, idx=2),
        Stroke(start_index=40, end_index=60, start_price=80, end_price=100, direction=1, idx=3),
    ]
    
    is_valid, errors = SegmentValidator.validate_segment_continuity(continuous_segments)
    print(f"连续线段验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    # 创建不连续的线段
    discontinuous_segments = [
        Stroke(start_index=0, end_index=20, start_price=100, end_price=120, direction=1, idx=1),
        Stroke(start_index=25, end_index=40, start_price=120, end_price=80, direction=-1, idx=2),  # 不连续
        Stroke(start_index=40, end_index=60, start_price=80, end_price=100, direction=1, idx=3),
    ]
    
    is_valid, errors = SegmentValidator.validate_segment_continuity(discontinuous_segments)
    print(f"不连续线段验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    print("✅ 线段连续性验证测试完成\n")


def test_direction_alternation_validation():
    """测试方向交替性验证"""
    print("=== 测试方向交替性验证 ===")
    
    # 创建方向交替的线段
    alternating_segments = [
        Stroke(start_index=0, end_index=20, start_price=100, end_price=120, direction=1, idx=1),
        Stroke(start_index=20, end_index=40, start_price=120, end_price=80, direction=-1, idx=2),
        Stroke(start_index=40, end_index=60, start_price=80, end_price=100, direction=1, idx=3),
    ]
    
    is_valid, errors = SegmentValidator.validate_segment_direction_alternation(alternating_segments)
    print(f"方向交替验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    # 创建方向不交替的线段
    non_alternating_segments = [
        Stroke(start_index=0, end_index=20, start_price=100, end_price=120, direction=1, idx=1),
        Stroke(start_index=20, end_index=40, start_price=120, end_price=140, direction=1, idx=2),  # 同向
        Stroke(start_index=40, end_index=60, start_price=140, end_price=100, direction=-1, idx=3),
    ]
    
    is_valid, errors = SegmentValidator.validate_segment_direction_alternation(non_alternating_segments)
    print(f"方向不交替验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    print("✅ 方向交替性验证测试完成\n")


def test_comprehensive_validation():
    """测试综合验证"""
    print("=== 测试综合验证 ===")
    
    # 创建测试数据
    strokes = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=105, direction=1, idx=1),
        Stroke(start_index=5, end_index=8, start_price=105, end_price=102, direction=-1, idx=2),
        Stroke(start_index=8, end_index=12, start_price=102, end_price=110, direction=1, idx=3),
        Stroke(start_index=12, end_index=15, start_price=110, end_price=108, direction=-1, idx=4),
        Stroke(start_index=15, end_index=20, start_price=108, end_price=115, direction=1, idx=5),
    ]
    
    segments = [
        Stroke(start_index=0, end_index=20, start_price=100, end_price=115, direction=1, idx=1),
    ]
    
    is_valid, errors = SegmentValidator.validate_all(strokes, segments)
    print(f"综合验证: {'通过' if is_valid else '失败'}")
    if errors:
        print("发现错误:")
        for error in errors:
            print(f"  - {error}")
    
    print("✅ 综合验证测试完成\n")


def main():
    """主测试函数"""
    print("🚀 开始线段验证器测试...\n")
    
    test_stroke_continuity_validation()
    test_segment_continuity_validation()
    test_direction_alternation_validation()
    test_comprehensive_validation()
    
    print("🎉 线段验证器测试完成！")


if __name__ == "__main__":
    main()