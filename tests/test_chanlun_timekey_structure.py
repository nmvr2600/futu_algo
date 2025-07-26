#!/usr/bin/env python3
"""
缠论time_key数据结构测试
验证基于time_key的新数据结构设计
"""

import pandas as pd
import numpy as np
import sys
import os
import unittest
from datetime import datetime

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import (
    ChanlunProcessor,
    Fractal,
    FractalType,
    Stroke,
    Central,
)


class TestChanlunTimeKeyStructure(unittest.TestCase):
    """测试基于time_key的数据结构设计"""

    def setUp(self):
        """设置测试数据"""
        self.processor = ChanlunProcessor()
        
    def create_test_data_with_unique_timekeys(self):
        """创建具有唯一time_key的测试数据"""
        dates = pd.date_range("2024-01-01", periods=20, freq="D")
        data = {
            "time_key": dates,
            "open": [10.0, 11.0, 12.0, 11.0, 10.0, 9.0, 8.0, 9.0, 10.0, 11.0,
                     12.0, 11.0, 10.0, 9.0, 8.0, 9.0, 10.0, 11.0, 12.0, 11.0],
            "high": [11.0, 12.0, 13.0, 12.0, 11.0, 10.0, 9.0, 10.0, 11.0, 12.0,
                     13.0, 12.0, 11.0, 10.0, 9.0, 10.0, 11.0, 12.0, 13.0, 12.0],
            "low": [9.0, 10.0, 11.0, 10.0, 9.0, 8.0, 7.0, 8.0, 9.0, 10.0,
                    11.0, 10.0, 9.0, 8.0, 7.0, 8.0, 9.0, 10.0, 11.0, 10.0],
            "close": [10.5, 11.5, 12.5, 11.5, 10.5, 9.5, 8.5, 9.5, 10.5, 11.5,
                      12.5, 11.5, 10.5, 9.5, 8.5, 9.5, 10.5, 11.5, 12.5, 11.5],
        }
        return pd.DataFrame(data)

    def test_timekey_uniqueness(self):
        """测试time_key的唯一性"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 验证time_key唯一性
        self.assertEqual(len(df["time_key"].unique()), len(df))
        self.assertTrue(df["time_key"].is_monotonic_increasing)

    def test_fractal_timekey_reference(self):
        """测试分型使用time_key作为标识"""
        df = self.create_test_data_with_unique_timekeys()
        result = self.processor.process(df)
        
        # 验证分型结果
        fractals = result['fractals']
        self.assertIsInstance(fractals, list)
        
        # 验证每个分型都有对应的time_key引用
        for fractal in fractals:
            # 在当前实现中，我们仍然使用index，但将来会改为time_key
            self.assertTrue(hasattr(fractal, 'index'))
            self.assertTrue(hasattr(fractal, 'type'))
            self.assertTrue(hasattr(fractal, 'price'))

    def test_stroke_timekey_reference(self):
        """测试笔使用time_key作为起止标识"""
        df = self.create_test_data_with_unique_timekeys()
        result = self.processor.process(df)
        
        # 验证笔结果
        strokes = result['strokes']
        if len(strokes) > 0:
            stroke = strokes[0]
            # 验证笔有起止索引
            self.assertTrue(hasattr(stroke, 'start_index'))
            self.assertTrue(hasattr(stroke, 'end_index'))
            self.assertTrue(hasattr(stroke, 'start_price'))
            self.assertTrue(hasattr(stroke, 'end_price'))
            self.assertTrue(hasattr(stroke, 'direction'))

    def test_new_fractal_structure_with_timekey(self):
        """测试新的分型结构设计"""
        # 创建模拟的time_key
        time_keys = pd.date_range("2024-01-01", periods=5, freq="D")
        
        # 测试分型数据结构
        fractal = Fractal(
            index=2,  # 在合并数据中的索引
            type=FractalType.TOP,
            price=12.5,
            idx=1
        )
        
        # 验证分型属性
        self.assertEqual(fractal.index, 2)
        self.assertEqual(fractal.type, FractalType.TOP)
        self.assertEqual(fractal.price, 12.5)
        self.assertEqual(fractal.idx, 1)

    def test_new_stroke_structure_with_timekey(self):
        """测试新的笔结构设计"""
        # 测试笔数据结构
        stroke = Stroke(
            start_index=1,
            end_index=3,
            start_price=10.0,
            end_price=12.0,
            direction=1,
            idx=1
        )
        
        # 验证笔属性
        self.assertEqual(stroke.start_index, 1)
        self.assertEqual(stroke.end_index, 3)
        self.assertEqual(stroke.start_price, 10.0)
        self.assertEqual(stroke.end_price, 12.0)
        self.assertEqual(stroke.direction, 1)
        self.assertEqual(stroke.idx, 1)

    def test_timekey_based_visualization_mapping(self):
        """测试基于time_key的可视化映射"""
        df = self.create_test_data_with_unique_timekeys()
        result = self.processor.process(df)
        
        # 验证原始数据和处理结果的一致性
        self.assertIn('merged_df', result)
        self.assertIn('fractals', result)
        self.assertIn('strokes', result)
        
        # 验证time_key在原始数据中存在
        self.assertIn('time_key', df.columns)
        
        # 验证处理后的数据也有time_key
        if result['merged_df'] is not None and len(result['merged_df']) > 0:
            self.assertIn('time_key', result['merged_df'].columns)

    def test_timekey_consistency_across_levels(self):
        """测试各层级time_key引用的一致性"""
        df = self.create_test_data_with_unique_timekeys()
        result = self.processor.process(df)
        
        # 获取处理结果
        merged_df = result['merged_df']
        fractals = result['fractals']
        strokes = result['strokes']
        
        if merged_df is not None and len(merged_df) > 0:
            # 验证分型索引在合并数据范围内
            for fractal in fractals:
                self.assertGreaterEqual(fractal.index, 0)
                self.assertLess(fractal.index, len(merged_df))
            
            # 验证笔索引在合并数据范围内
            for stroke in strokes:
                self.assertGreaterEqual(stroke.start_index, 0)
                self.assertLess(stroke.start_index, len(merged_df))
                self.assertGreaterEqual(stroke.end_index, 0)
                self.assertLess(stroke.end_index, len(merged_df))

    def test_edge_case_empty_data(self):
        """测试空数据情况"""
        empty_df = pd.DataFrame({
            "time_key": pd.to_datetime([]),
            "open": [],
            "high": [],
            "low": [],
            "close": []
        })
        
        result = self.processor.process(empty_df)
        
        # 验证返回结果结构
        self.assertIn('fractals', result)
        self.assertIn('strokes', result)
        self.assertIn('segments', result)
        self.assertIn('centrals', result)
        
        # 验证空结果
        self.assertEqual(len(result['fractals']), 0)
        self.assertEqual(len(result['strokes']), 0)
        self.assertEqual(len(result['segments']), 0)
        self.assertEqual(len(result['centrals']), 0)

    def test_edge_case_single_point(self):
        """测试单点数据情况"""
        single_df = pd.DataFrame({
            "time_key": pd.to_datetime(["2024-01-01"]),
            "open": [10.0],
            "high": [11.0],
            "low": [9.0],
            "close": [10.5]
        })
        
        result = self.processor.process(single_df)
        
        # 验证返回结果结构
        self.assertIn('fractals', result)
        self.assertIn('strokes', result)
        
        # 单点数据应该无法形成分型和笔
        self.assertEqual(len(result['fractals']), 0)
        self.assertEqual(len(result['strokes']), 0)


if __name__ == "__main__":
    unittest.main()