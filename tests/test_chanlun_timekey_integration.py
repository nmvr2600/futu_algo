#!/usr/bin/env python3
"""
缠论time_key集成测试
验证基于time_key的新数据结构在完整流程中的工作情况
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


class TestChanlunTimeKeyIntegration(unittest.TestCase):
    """测试基于time_key的数据结构在完整流程中的集成"""

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

    def test_full_process_with_timekey(self):
        """测试完整处理流程中time_key的使用"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 执行完整处理流程
        result = self.processor.process(df)
        
        # 验证处理结果包含新的time_key字段
        fractals = result['fractals']
        strokes = result['strokes']
        segments = result['segments']
        centrals = result['centrals']
        
        # 验证分型包含time_key
        for fractal in fractals:
            self.assertTrue(hasattr(fractal, 'time_key'))
            self.assertIsNotNone(fractal.time_key)
            # 验证time_key是有效的datetime对象
            self.assertIsInstance(fractal.time_key, pd.Timestamp)
            
        # 验证笔包含time_key引用
        for stroke in strokes:
            self.assertTrue(hasattr(stroke, 'start_time_key'))
            self.assertTrue(hasattr(stroke, 'end_time_key'))
            self.assertIsNotNone(stroke.start_time_key)
            self.assertIsNotNone(stroke.end_time_key)
            # 验证time_key是有效的datetime对象
            self.assertIsInstance(stroke.start_time_key, pd.Timestamp)
            self.assertIsInstance(stroke.end_time_key, pd.Timestamp)
            
        # 验证线段包含time_key引用
        for segment in segments:
            self.assertTrue(hasattr(segment, 'start_time_key'))
            self.assertTrue(hasattr(segment, 'end_time_key'))
            self.assertIsNotNone(segment.start_time_key)
            self.assertIsNotNone(segment.end_time_key)
            # 验证time_key是有效的datetime对象
            self.assertIsInstance(segment.start_time_key, pd.Timestamp)
            self.assertIsInstance(segment.end_time_key, pd.Timestamp)
            
        # 验证中枢包含time_key引用
        for central in centrals:
            self.assertTrue(hasattr(central, 'start_time_key'))
            self.assertTrue(hasattr(central, 'end_time_key'))
            # 注意：中枢可能为空，所以这里允许为None
            if central.start_time_key is not None:
                self.assertIsInstance(central.start_time_key, pd.Timestamp)
            if central.end_time_key is not None:
                self.assertIsInstance(central.end_time_key, pd.Timestamp)

    def test_timekey_consistency_in_merged_data(self):
        """测试合并数据中time_key的一致性"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 执行处理
        result = self.processor.process(df)
        merged_df = result['merged_df']
        
        # 验证合并后的数据仍然包含time_key列
        self.assertIn('time_key', merged_df.columns)
        
        # 验证time_key列不为空
        self.assertFalse(merged_df['time_key'].isnull().all())
        
        # 验证time_key是递增的（因为数据是按时间排序的）
        self.assertTrue(merged_df['time_key'].is_monotonic_increasing)

    def test_fractal_timekey_mapping(self):
        """测试分型time_key与原始数据的映射关系"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 执行处理
        result = self.processor.process(df)
        fractals = result['fractals']
        merged_df = result['merged_df']
        
        # 验证每个分型的time_key都能在合并数据中找到
        for fractal in fractals:
            # 查找对应的索引
            matching_indices = merged_df[merged_df['time_key'] == fractal.time_key].index.tolist()
            self.assertGreater(len(matching_indices), 0, 
                             f"分型time_key {fractal.time_key} 在合并数据中未找到")
            
            # 验证索引位置与分型索引一致
            if len(matching_indices) > 0:
                self.assertEqual(matching_indices[0], fractal.index,
                               f"分型索引 {fractal.index} 与time_key查找的索引 {matching_indices[0]} 不一致")

    def test_stroke_timekey_references(self):
        """测试笔对分型time_key的引用"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 执行处理
        result = self.processor.process(df)
        fractals = result['fractals']
        strokes = result['strokes']
        
        if len(strokes) > 0:
            stroke = strokes[0]
            
            # 验证笔的起始和结束time_key引用
            self.assertIsNotNone(stroke.start_time_key)
            self.assertIsNotNone(stroke.end_time_key)
            
            # 验证这些time_key在分型中存在
            start_time_key_found = any(f.time_key == stroke.start_time_key for f in fractals)
            end_time_key_found = any(f.time_key == stroke.end_time_key for f in fractals)
            
            self.assertTrue(start_time_key_found, 
                          f"笔的起始time_key {stroke.start_time_key} 在分型中未找到")
            self.assertTrue(end_time_key_found, 
                          f"笔的结束time_key {stroke.end_time_key} 在分型中未找到")

    def test_central_timekey_references(self):
        """测试中枢对笔time_key的引用"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 执行处理
        result = self.processor.process(df)
        strokes = result['strokes']
        centrals = result['centrals']
        
        # 如果有中枢，验证其time_key引用
        for central in centrals:
            if central.start_time_key is not None and central.end_time_key is not None:
                # 验证这些time_key在笔中存在
                start_time_key_found = any(s.start_time_key == central.start_time_key for s in strokes)
                end_time_key_found = any(s.end_time_key == central.end_time_key for s in strokes)
                
                self.assertTrue(start_time_key_found, 
                              f"中枢的起始time_key {central.start_time_key} 在笔中未找到")
                self.assertTrue(end_time_key_found, 
                              f"中枢的结束time_key {central.end_time_key} 在笔中未找到")

    def test_timekey_based_visualization_compatibility(self):
        """测试基于time_key的可视化兼容性"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 执行处理
        result = self.processor.process(df)
        
        # 验证结果结构兼容可视化需求
        self.assertIn('fractals', result)
        self.assertIn('strokes', result)
        self.assertIn('segments', result)
        self.assertIn('centrals', result)
        self.assertIn('merged_df', result)
        
        # 验证数据类型正确
        self.assertIsInstance(result['fractals'], list)
        self.assertIsInstance(result['strokes'], list)
        self.assertIsInstance(result['segments'], list)
        self.assertIsInstance(result['centrals'], list)
        self.assertIsInstance(result['merged_df'], pd.DataFrame)
        
        # 验证关键字段存在
        merged_df = result['merged_df']
        self.assertIn('time_key', merged_df.columns)
        self.assertIn('open', merged_df.columns)
        self.assertIn('high', merged_df.columns)
        self.assertIn('low', merged_df.columns)
        self.assertIn('close', merged_df.columns)


if __name__ == "__main__":
    unittest.main()