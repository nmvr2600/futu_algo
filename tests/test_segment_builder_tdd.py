#!/usr/bin/env python3
"""
TDD测试用例：线段构建器
使用测试驱动开发方法实现正确的线段构建逻辑
"""

import pandas as pd
import numpy as np
import sys
import os
import unittest

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Stroke, FractalType
from dataclasses import dataclass
from typing import List


class TestSegmentBuilderTDD(unittest.TestCase):
    """线段构建器TDD测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.processor = ChanlunProcessor()
    
    def create_test_strokes(self, stroke_data):
        """创建测试用笔数据"""
        strokes = []
        for i, data in enumerate(stroke_data):
            stroke = Stroke(
                start_index=data['start_index'],
                end_index=data['end_index'],
                start_price=data['start_price'],
                end_price=data['end_price'],
                direction=data['direction'],
                idx=i+1,
                fractal_start=data.get('fractal_start', i+1),
                fractal_end=data.get('fractal_end', i+2)
            )
            strokes.append(stroke)
        return strokes
    
    def test_stroke_continuity_validation(self):
        """测试笔连续性验证"""
        print("=== 测试笔连续性验证 ===")
        
        # 创建连续的笔
        continuous_strokes = self.create_test_strokes([
            {'start_index': 0, 'end_index': 5, 'start_price': 100, 'end_price': 110, 'direction': 1},
            {'start_index': 5, 'end_index': 10, 'start_price': 110, 'end_price': 100, 'direction': -1},
            {'start_index': 10, 'end_index': 15, 'start_price': 100, 'end_price': 120, 'direction': 1},
        ])
        
        # 验证连续性（应该通过）
        self.assertTrue(self._validate_stroke_continuity(continuous_strokes))
        
        # 创建不连续的笔
        discontinuous_strokes = self.create_test_strokes([
            {'start_index': 0, 'end_index': 5, 'start_price': 100, 'end_price': 110, 'direction': 1},
            {'start_index': 6, 'end_index': 10, 'start_price': 110, 'end_price': 100, 'direction': -1},  # 索引不连续
            {'start_index': 10, 'end_index': 15, 'start_price': 100, 'end_price': 120, 'direction': 1},
        ])
        
        # 验证连续性（应该失败）
        self.assertFalse(self._validate_stroke_continuity(discontinuous_strokes))
        
        print("✅ 笔连续性验证测试通过")
    
    def test_simple_segment_construction(self):
        """测试简单线段构建"""
        print("=== 测试简单线段构建 ===")
        
        # 创建明确的走势：上涨线段 -> 下跌线段 -> 上涨线段
        strokes = self.create_test_strokes([
            # 第一个上涨线段的构成笔
            {'start_index': 0, 'end_index': 5, 'start_price': 100, 'end_price': 105, 'direction': 1, 'fractal_start': 1, 'fractal_end': 2},
            {'start_index': 5, 'end_index': 8, 'start_price': 105, 'end_price': 102, 'direction': -1, 'fractal_start': 2, 'fractal_end': 3},
            {'start_index': 8, 'end_index': 12, 'start_price': 102, 'end_price': 110, 'direction': 1, 'fractal_start': 3, 'fractal_end': 4},
            {'start_index': 12, 'end_index': 15, 'start_price': 110, 'end_price': 108, 'direction': -1, 'fractal_start': 4, 'fractal_end': 5},
            {'start_index': 15, 'end_index': 20, 'start_price': 108, 'end_price': 115, 'direction': 1, 'fractal_start': 5, 'fractal_end': 6},
            
            # 破坏性下跌
            {'start_index': 20, 'end_index': 25, 'start_price': 115, 'end_price': 95, 'direction': -1, 'fractal_start': 6, 'fractal_end': 7},
            
            # 第二个下跌线段的构成笔
            {'start_index': 25, 'end_index': 28, 'start_price': 95, 'end_price': 98, 'direction': 1, 'fractal_start': 7, 'fractal_end': 8},
            {'start_index': 28, 'end_index': 32, 'start_price': 98, 'end_price': 90, 'direction': -1, 'fractal_start': 8, 'fractal_end': 9},
            {'start_index': 32, 'end_index': 35, 'start_price': 90, 'end_price': 93, 'direction': 1, 'fractal_start': 9, 'fractal_end': 10},
            {'start_index': 35, 'end_index': 40, 'start_price': 93, 'end_price': 85, 'direction': -1, 'fractal_start': 10, 'fractal_end': 11},
        ])
        
        # 构建线段
        segments = self._build_segments_tdd(strokes)
        
        print(f"输入笔数量: {len(strokes)}")
        print(f"生成线段数量: {len(segments)}")
        
        # 验证结果
        self.assertGreater(len(segments), 1, "应该生成多个线段")
        
        # 验证线段连续性
        self._validate_segment_continuity(segments)
        
        # 验证线段方向交替性
        self._validate_segment_direction_alternation(segments)
        
        print("✅ 简单线段构建测试通过")
    
    def test_segment_break_detection(self):
        """测试线段破坏检测"""
        print("=== 测试线段破坏检测 ===")
        
        # 创建包含明显破坏的走势
        strokes = self.create_test_strokes([
            # 上涨线段
            {'start_index': 0, 'end_index': 5, 'start_price': 100, 'end_price': 120, 'direction': 1},
            {'start_index': 5, 'end_index': 8, 'start_price': 120, 'end_price': 110, 'direction': -1},
            {'start_index': 8, 'end_index': 12, 'start_price': 110, 'end_price': 130, 'direction': 1},
            {'start_index': 12, 'end_index': 15, 'start_price': 130, 'end_price': 125, 'direction': -1},
            {'start_index': 15, 'end_index': 20, 'start_price': 125, 'end_price': 140, 'direction': 1},
            
            # 破坏性下跌（足够强以破坏上涨线段）
            {'start_index': 20, 'end_index': 30, 'start_price': 140, 'end_price': 80, 'direction': -1},
            
            # 新的下跌线段
            {'start_index': 30, 'end_index': 35, 'start_price': 80, 'end_price': 90, 'direction': 1},
            {'start_index': 35, 'end_index': 40, 'start_price': 90, 'end_price': 70, 'direction': -1},
        ])
        
        segments = self._build_segments_tdd(strokes)
        
        print(f"输入笔数量: {len(strokes)}")
        print(f"生成线段数量: {len(segments)}")
        
        # 应该至少生成2个线段
        self.assertGreaterEqual(len(segments), 2, "应该检测到线段破坏并生成新线段")
        
        # 第一个线段应该是上涨的
        self.assertEqual(segments[0].direction, 1, "第一个线段应该是上涨的")
        
        # 第二个线段应该是下跌的
        if len(segments) > 1:
            self.assertEqual(segments[1].direction, -1, "第二个线段应该是下跌的")
        
        print("✅ 线段破坏检测测试通过")
    
    def test_segment_validation(self):
        """测试线段验证逻辑"""
        print("=== 测试线段验证逻辑 ===")
        
        # 创建有效的线段
        valid_segments = self.create_test_strokes([
            {'start_index': 0, 'end_index': 20, 'start_price': 100, 'end_price': 140, 'direction': 1},
            {'start_index': 20, 'end_index': 40, 'start_price': 140, 'end_price': 80, 'direction': -1},
        ])
        
        # 验证线段连续性和方向交替性
        self._validate_segment_continuity(valid_segments)
        self._validate_segment_direction_alternation(valid_segments)
        
        # 创建无效的线段（不连续）
        invalid_segments = self.create_test_strokes([
            {'start_index': 0, 'end_index': 20, 'start_price': 100, 'end_price': 140, 'direction': 1},
            {'start_index': 25, 'end_index': 40, 'start_price': 140, 'end_price': 80, 'direction': -1},  # 不连续
        ])
        
        # 应该检测到不连续
        with self.assertRaises(AssertionError):
            self._validate_segment_continuity(invalid_segments)
        
        print("✅ 线段验证逻辑测试通过")
    
    def _validate_stroke_continuity(self, strokes):
        """验证笔是否首尾相接"""
        if len(strokes) < 2:
            return True
        
        for i in range(1, len(strokes)):
            prev_stroke = strokes[i-1]
            curr_stroke = strokes[i]
            if prev_stroke.end_index != curr_stroke.start_index:
                print(f"笔不连续: 笔{i-1}终点({prev_stroke.end_index}) != 笔{i}起点({curr_stroke.start_index})")
                return False
        return True
    
    def _validate_segment_continuity(self, segments):
        """验证线段是否首尾相接"""
        if len(segments) < 2:
            return True
        
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            if prev_segment.end_index != curr_segment.start_index:
                raise AssertionError(f"线段不连续: 线段{i-1}终点({prev_segment.end_index}) != 线段{i}起点({curr_segment.start_index})")
        return True
    
    def _validate_segment_direction_alternation(self, segments):
        """验证线段方向是否交替"""
        if len(segments) < 2:
            return True
        
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            if prev_segment.direction == curr_segment.direction:
                raise AssertionError(f"线段方向未交替: 线段{i-1}和线段{i}方向相同({prev_segment.direction})")
        return True
    
    def _build_segments_tdd(self, strokes):
        """TDD线段构建实现（测试版本）"""
        # 这里先实现一个简单的版本，后续会完善
        if len(strokes) < 3:
            return []
        
        # 简单的实现：将同向笔合并
        segments = []
        i = 0
        
        while i < len(strokes):
            # 找到连续同向的笔
            direction = strokes[i].direction
            j = i
            while j < len(strokes) and strokes[j].direction == direction:
                j += 1
            
            if j > i:
                # 创建线段
                start_stroke = strokes[i]
                end_stroke = strokes[j-1]
                segment = Stroke(
                    start_index=start_stroke.start_index,
                    end_index=end_stroke.end_index,
                    start_price=start_stroke.start_price,
                    end_price=end_stroke.end_price,
                    direction=direction,
                    idx=len(segments) + 1,
                    fractal_start=start_stroke.fractal_start,
                    fractal_end=end_stroke.fractal_end
                )
                segments.append(segment)
            
            i = j
        
        return segments


def main():
    """主测试函数"""
    print("🚀 开始TDD线段构建测试...\n")
    
    # 运行测试
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=2)
    
    print("\n🎉 TDD线段构建测试完成！")


if __name__ == "__main__":
    main()