#!/usr/bin/env python3
"""
测试笔连续性验证功能
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import Stroke, FractalType
from util.stroke_validator import StrokeValidator


def test_stroke_continuity_validation():
    """测试笔连续性验证"""
    print("=== 测试笔连续性验证 ===")
    
    # 创建测试数据 - 连续的笔
    continuous_strokes = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=120, direction=1, idx=1, fractal_start=1, fractal_end=2),
        Stroke(start_index=5, end_index=10, start_price=120, end_price=100, direction=-1, idx=2, fractal_start=2, fractal_end=3),
        Stroke(start_index=10, end_index=15, start_price=100, end_price=130, direction=1, idx=3, fractal_start=3, fractal_end=4),
    ]
    
    print("测试连续的笔:")
    is_continuous, msg = StrokeValidator.validate_stroke_continuity(continuous_strokes)
    print(f"  结果: {'通过' if is_continuous else '失败'} - {msg}")
    
    # 创建测试数据 - 不连续的笔（索引不连续）
    discontinuous_strokes_by_index = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=120, direction=1, idx=1, fractal_start=1, fractal_end=2),
        Stroke(start_index=6, end_index=10, start_price=120, end_price=100, direction=-1, idx=2, fractal_start=2, fractal_end=3),  # 起始索引应该是5
        Stroke(start_index=10, end_index=15, start_price=100, end_price=130, direction=1, idx=3, fractal_start=3, fractal_end=4),
    ]
    
    print("\n测试索引不连续的笔:")
    is_continuous, msg = StrokeValidator.validate_stroke_continuity(discontinuous_strokes_by_index)
    print(f"  结果: {'通过' if is_continuous else '失败'} - {msg}")
    
    # 创建测试数据 - 不连续的笔（方向相同）
    discontinuous_strokes_by_direction = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=120, direction=1, idx=1, fractal_start=1, fractal_end=2),
        Stroke(start_index=5, end_index=10, start_price=120, end_price=130, direction=1, idx=2, fractal_start=2, fractal_end=3),  # 方向应该相反
        Stroke(start_index=10, end_index=15, start_price=130, end_price=100, direction=-1, idx=3, fractal_start=3, fractal_end=4),
    ]
    
    print("\n测试方向相同的笔:")
    is_continuous, msg = StrokeValidator.validate_stroke_continuity(discontinuous_strokes_by_direction)
    print(f"  结果: {'通过' if is_continuous else '失败'} - {msg}")
    
    # 创建测试数据 - 不连续的笔（分型编号不连续）
    discontinuous_strokes_by_fractal = [
        Stroke(start_index=0, end_index=5, start_price=100, end_price=120, direction=1, idx=1, fractal_start=1, fractal_end=2),
        Stroke(start_index=5, end_index=10, start_price=120, end_price=100, direction=-1, idx=2, fractal_start=3, fractal_end=4),  # 起始分型应该是2
        Stroke(start_index=10, end_index=15, start_price=100, end_price=130, direction=1, idx=3, fractal_start=4, fractal_end=5),
    ]
    
    print("\n测试分型编号不连续的笔:")
    is_continuous, msg = StrokeValidator.validate_stroke_continuity(discontinuous_strokes_by_fractal)
    print(f"  结果: {'通过' if is_continuous else '失败'} - {msg}")


def main():
    """主测试函数"""
    test_stroke_continuity_validation()


if __name__ == "__main__":
    main()