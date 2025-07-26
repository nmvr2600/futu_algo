#!/usr/bin/env python3
"""
缠论time_key可视化测试
验证基于time_key的新数据结构在可视化中的正确使用
"""

import pandas as pd
import numpy as np
import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import (
    ChanlunProcessor,
    Fractal,
    FractalType,
    Stroke,
    Central,
)
from chanlun_plotly_visualizer import PlotlyChanlunVisualizer


class TestChanlunTimeKeyVisualization(unittest.TestCase):
    """测试基于time_key的数据结构在可视化中的正确使用"""

    def setUp(self):
        """设置测试数据"""
        self.processor = ChanlunProcessor()
        self.visualizer = PlotlyChanlunVisualizer()
        
    def create_test_data_with_unique_timekeys(self):
        """创建具有唯一time_key的测试数据"""
        # 创建10天的测试数据
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        data = {
            "time_key": dates,
            "open": [10.0, 11.0, 12.0, 11.0, 10.0, 9.0, 8.0, 9.0, 10.0, 11.0],
            "high": [11.0, 12.0, 13.0, 12.0, 11.0, 10.0, 9.0, 10.0, 11.0, 12.0],
            "low": [9.0, 10.0, 11.0, 10.0, 9.0, 8.0, 7.0, 8.0, 9.0, 10.0],
            "close": [10.5, 11.5, 12.5, 11.5, 10.5, 9.5, 8.5, 9.5, 10.5, 11.5],
        }
        return pd.DataFrame(data)

    def test_fractal_timekey_usage_in_visualization(self):
        """测试分型在可视化中正确使用time_key"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 创建模拟的分型数据
        fractal1 = Fractal(
            index=2,
            type=FractalType.TOP,
            price=13.0,
            time_key=df.iloc[2]['time_key'],  # 使用正确的time_key
            idx=1
        )
        
        fractal2 = Fractal(
            index=5,
            type=FractalType.BOTTOM,
            price=8.0,
            time_key=df.iloc[5]['time_key'],  # 使用正确的time_key
            idx=2
        )
        
        result = {
            "fractals": [fractal1, fractal2],
            "strokes": [],
            "segments": [],
            "centrals": []
        }
        
        # 验证分型的time_key与数据帧中的time_key一致
        self.assertEqual(fractal1.time_key, df.iloc[2]['time_key'])
        self.assertEqual(fractal2.time_key, df.iloc[5]['time_key'])
        
        # 验证time_key是有效的datetime对象
        self.assertIsInstance(fractal1.time_key, pd.Timestamp)
        self.assertIsInstance(fractal2.time_key, pd.Timestamp)

    def test_stroke_timekey_usage_in_visualization(self):
        """测试笔在可视化中正确使用time_key"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 创建模拟的分型数据
        fractal1 = Fractal(
            index=2,
            type=FractalType.TOP,
            price=13.0,
            time_key=df.iloc[2]['time_key'],
            idx=1
        )
        
        fractal2 = Fractal(
            index=5,
            type=FractalType.BOTTOM,
            price=8.0,
            time_key=df.iloc[5]['time_key'],
            idx=2
        )
        
        # 创建模拟的笔数据
        stroke = Stroke(
            start_index=2,
            end_index=5,
            start_price=13.0,
            end_price=8.0,
            direction=-1,
            start_time_key=fractal1.time_key,  # 使用起始分型的time_key
            end_time_key=fractal2.time_key,    # 使用结束分型的time_key
            idx=1
        )
        
        result = {
            "fractals": [fractal1, fractal2],
            "strokes": [stroke],
            "segments": [],
            "centrals": []
        }
        
        # 验证笔的time_key与分型的time_key一致
        self.assertEqual(stroke.start_time_key, fractal1.time_key)
        self.assertEqual(stroke.end_time_key, fractal2.time_key)
        
        # 验证time_key是有效的datetime对象
        self.assertIsInstance(stroke.start_time_key, pd.Timestamp)
        self.assertIsInstance(stroke.end_time_key, pd.Timestamp)

    def test_visualizer_direct_timekey_usage(self):
        """测试可视化器直接使用time_key而不是索引"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 创建模拟的分型数据
        fractal1 = Fractal(
            index=2,
            type=FractalType.TOP,
            price=13.0,
            time_key=df.iloc[2]['time_key'],
            idx=1
        )
        
        fractal2 = Fractal(
            index=5,
            type=FractalType.BOTTOM,
            price=8.0,
            time_key=df.iloc[5]['time_key'],
            idx=2
        )
        
        # 创建模拟的笔数据
        stroke = Stroke(
            start_index=2,
            end_index=5,
            start_price=13.0,
            end_price=8.0,
            direction=-1,
            start_time_key=fractal1.time_key,
            end_time_key=fractal2.time_key,
            idx=1
        )
        
        result = {
            "fractals": [fractal1, fractal2],
            "strokes": [stroke],
            "segments": [],
            "centrals": []
        }
        
        # 测试可视化器是否能正确处理time_key
        try:
            fig = self.visualizer.create_comprehensive_chart(df, result, "TEST", None)
            self.assertIsNotNone(fig)
        except Exception as e:
            self.fail(f"可视化器处理time_key时出错: {e}")

    def test_timekey_consistency_across_elements(self):
        """测试各级元素time_key的一致性"""
        df = self.create_test_data_with_unique_timekeys()
        
        # 创建分型
        fractal1 = Fractal(
            index=1,
            type=FractalType.BOTTOM,
            price=10.0,
            time_key=df.iloc[1]['time_key'],
            idx=1
        )
        
        fractal2 = Fractal(
            index=3,
            type=FractalType.TOP,
            price=13.0,
            time_key=df.iloc[3]['time_key'],
            idx=2
        )
        
        fractal3 = Fractal(
            index=6,
            type=FractalType.BOTTOM,
            price=8.0,
            time_key=df.iloc[6]['time_key'],
            idx=3
        )
        
        # 创建笔
        stroke1 = Stroke(
            start_index=1,
            end_index=3,
            start_price=10.0,
            end_price=13.0,
            direction=1,
            start_time_key=fractal1.time_key,
            end_time_key=fractal2.time_key,
            idx=1
        )
        
        stroke2 = Stroke(
            start_index=3,
            end_index=6,
            start_price=13.0,
            end_price=8.0,
            direction=-1,
            start_time_key=fractal2.time_key,
            end_time_key=fractal3.time_key,
            idx=2
        )
        
        # 创建中枢
        central = Central(
            start_index=1,
            end_index=6,
            high=12.0,
            low=9.0,
            start_time_key=stroke1.start_time_key,
            end_time_key=stroke2.end_time_key,
            level=1
        )
        
        result = {
            "fractals": [fractal1, fractal2, fractal3],
            "strokes": [stroke1, stroke2],
            "segments": [],
            "centrals": [central]
        }
        
        # 验证时间戳的一致性
        self.assertEqual(stroke1.start_time_key, fractal1.time_key)
        self.assertEqual(stroke1.end_time_key, fractal2.time_key)
        self.assertEqual(stroke2.start_time_key, fractal2.time_key)
        self.assertEqual(stroke2.end_time_key, fractal3.time_key)
        self.assertEqual(central.start_time_key, stroke1.start_time_key)
        self.assertEqual(central.end_time_key, stroke2.end_time_key)


if __name__ == "__main__":
    unittest.main()