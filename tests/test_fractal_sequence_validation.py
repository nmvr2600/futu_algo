#!/usr/bin/env python3
"""
测试分型连续性验证功能
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import Fractal, FractalType
from util.stroke_validator import StrokeValidator


def test_fractal_sequence_validation():
    """测试分型序列验证"""
    print("=== 测试分型序列验证 ===")
    
    # 创建测试数据 - 有效的分型序列
    valid_fractals = [
        Fractal(index=2, type=FractalType.TOP, price=106, idx=1),
        Fractal(index=5, type=FractalType.BOTTOM, price=99, idx=2),
        Fractal(index=8, type=FractalType.TOP, price=109, idx=3),
        Fractal(index=11, type=FractalType.BOTTOM, price=100, idx=4),
    ]
    
    print("测试有效的分型序列:")
    is_valid, msg = StrokeValidator.validate_fractal_sequence(valid_fractals)
    print(f"  结果: {'通过' if is_valid else '失败'} - {msg}")
    
    # 创建测试数据 - 相邻同类型分型
    invalid_fractals_same_type = [
        Fractal(index=2, type=FractalType.TOP, price=106, idx=1),
        Fractal(index=5, type=FractalType.TOP, price=108, idx=2),  # 相邻顶分型
        Fractal(index=8, type=FractalType.BOTTOM, price=99, idx=3),
    ]
    
    print("\n测试相邻同类型分型:")
    is_valid, msg = StrokeValidator.validate_fractal_sequence(invalid_fractals_same_type)
    print(f"  结果: {'通过' if is_valid else '失败'} - {msg}")
    
    # 创建测试数据 - 分型间隔不足
    invalid_fractals_close = [
        Fractal(index=2, type=FractalType.TOP, price=106, idx=1),
        Fractal(index=3, type=FractalType.BOTTOM, price=99, idx=2),  # 间隔只有1
        Fractal(index=5, type=FractalType.TOP, price=109, idx=3),
    ]
    
    print("\n测试分型间隔不足:")
    is_valid, msg = StrokeValidator.validate_fractal_sequence(invalid_fractals_close)
    print(f"  结果: {'通过' if is_valid else '失败'} - {msg}")


def main():
    """主测试函数"""
    test_fractal_sequence_validation()


if __name__ == "__main__":
    main()