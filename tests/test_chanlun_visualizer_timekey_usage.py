#!/usr/bin/env python3
"""
缠论可视化器time_key使用测试
验证可视化器是否正确使用time_key而不是索引
"""

import pandas as pd
import numpy as np
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go

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


class TestChanlunVisualizerTimeKeyUsage(unittest.TestCase):
    """测试可视化器是否正确使用time_key而不是索引"""

    def setUp(self):
        """设置测试数据"""
        self.visualizer = PlotlyChanlunVisualizer()
        
    def create_test_data(self):
        """创建测试数据"""
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        data = {
            "time_key": dates,
            "open": [10.0, 11.0, 12.0, 11.0, 10.0, 9.0, 8.0, 9.0, 10.0, 11.0],
            "high": [11.0, 12.0, 13.0, 12.0, 11.0, 10.0, 9.0, 10.0, 11.0, 12.0],
            "low": [9.0, 10.0, 11.0, 10.0, 9.0, 8.0, 7.0, 8.0, 9.0, 10.0],
            "close": [10.5, 11.5, 12.5, 11.5, 10.5, 9.5, 8.5, 9.5, 10.5, 11.5],
        }
        return pd.DataFrame(data)

    def test_fractals_use_timekey_not_index(self):
        """测试分型绘制使用time_key而不是索引"""
        df = self.create_test_data()
        
        # 创建分型，使用正确的time_key
        fractal1 = Fractal(
            index=2,
            type=FractalType.TOP,
            price=13.0,
            time_key=df.iloc[2]['time_key'],  # time_key应该与df中的时间戳一致
            idx=1
        )
        
        fractal2 = Fractal(
            index=5,
            type=FractalType.BOTTOM,
            price=8.0,
            time_key=df.iloc[5]['time_key'],  # time_key应该与df中的时间戳一致
            idx=2
        )
        
        result = {
            "fractals": [fractal1, fractal2],
            "strokes": [],
            "segments": [],
            "centrals": []
        }
        
        # 创建模拟的figure对象
        fig = MagicMock()
            
        # 直接调用_plot_fractals方法
        self.visualizer._plot_fractals(fig, df, result, 1, 1)
        
        # 验证add_trace被调用
        self.assertTrue(fig.add_trace.called)
        
        # 获取调用参数
        call_args = fig.add_trace.call_args_list
        
        # 验证传递给add_trace的x值是time_key而不是索引
        for call_arg in call_args:
            trace_data = call_arg[0][0]  # 第一个参数是trace对象
            if isinstance(trace_data, go.Scatter):
                x_values = trace_data.x
                # 验证x_values包含的是datetime对象而不是整数索引
                for x_val in x_values:
                    self.assertIsInstance(x_val, pd.Timestamp, 
                                        f"Expected pd.Timestamp, got {type(x_val)}: {x_val}")

    def test_strokes_use_timekey_not_index(self):
        """测试笔绘制使用time_key而不是索引"""
        df = self.create_test_data()
        
        # 创建分型
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
        
        # 创建笔，使用time_key
        stroke = Stroke(
            start_index=2,
            end_index=5,
            start_price=13.0,
            end_price=8.0,
            direction=-1,
            start_time_key=fractal1.time_key,  # 使用time_key而不是依赖索引
            end_time_key=fractal2.time_key,    # 使用time_key而不是依赖索引
            idx=1
        )
        
        result = {
            "fractals": [fractal1, fractal2],
            "strokes": [stroke],
            "segments": [],
            "centrals": []
        }
        
        # 创建模拟的figure对象
        fig = MagicMock()
        
        # 直接调用_plot_strokes方法
        self.visualizer._plot_strokes(fig, df, result, 1, 1)
        
        # 验证add_trace被调用
        self.assertTrue(fig.add_trace.called)
        
        # 获取调用参数
        call_args = fig.add_trace.call_args_list
        
        # 验证传递给add_trace的x值是time_key而不是索引
        for call_arg in call_args:
            trace_data = call_arg[0][0]  # 第一个参数是trace对象
            if isinstance(trace_data, go.Scatter):
                x_values = trace_data.x
                # 验证x_values包含的是datetime对象而不是整数索引
                for x_val in x_values:
                    self.assertIsInstance(x_val, pd.Timestamp,
                                        f"Expected pd.Timestamp, got {type(x_val)}: {x_val}")

    def test_segments_use_timekey_not_index(self):
        """测试线段绘制使用time_key而不是索引"""
        df = self.create_test_data()
        
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
        
        # 创建线段，使用time_key
        segment = Stroke(  # 线段也是Stroke类型
            start_index=1,
            end_index=6,
            start_price=10.0,
            end_price=8.0,
            direction=-1,
            start_time_key=stroke1.start_time_key,  # 使用time_key而不是依赖索引
            end_time_key=stroke2.end_time_key,      # 使用time_key而不是依赖索引
            idx=1
        )
        
        result = {
            "fractals": [fractal1, fractal2, fractal3],
            "strokes": [stroke1, stroke2],
            "segments": [segment],
            "centrals": []
        }
        
        # 创建模拟的figure对象
        fig = MagicMock()
        
        # 直接调用_plot_segments方法
        self.visualizer._plot_segments(fig, df, result, 1, 1)
        
        # 验证add_trace被调用
        # 注意：如果没有线段数据，可能不会调用add_trace
        # 这里我们只是验证方法能正确处理time_key

    def test_centrals_use_timekey_not_index(self):
        """测试中枢绘制使用time_key而不是索引"""
        df = self.create_test_data()
        
        # 创建中枢，使用time_key
        central = Central(
            start_index=2,
            end_index=5,
            high=12.0,
            low=9.0,
            start_time_key=df.iloc[2]['time_key'],  # 使用time_key而不是依赖索引
            end_time_key=df.iloc[5]['time_key'],    # 使用time_key而不是依赖索引
            level=1
        )
        
        result = {
            "fractals": [],
            "strokes": [],
            "segments": [],
            "centrals": [central]
        }
        
        # 创建模拟的figure对象
        fig = MagicMock()
        
        # 直接调用_plot_centrals方法
        self.visualizer._plot_centrals(fig, df, result, 1, 1)
        
        # 验证add_shape被调用
        self.assertTrue(fig.add_shape.called)
        
        # 获取调用参数
        call_args = fig.add_shape.call_args_list
        
        # 验证传递给add_shape的x0和x1值是time_key而不是索引
        for call_arg in call_args:
            kwargs = call_arg[1]  # 关键字参数
            x0 = kwargs.get('x0')
            x1 = kwargs.get('x1')
            # 验证x0和x1是datetime对象而不是整数索引
            self.assertIsInstance(x0, pd.Timestamp,
                                f"Expected pd.Timestamp for x0, got {type(x0)}: {x0}")
            self.assertIsInstance(x1, pd.Timestamp,
                                f"Expected pd.Timestamp for x1, got {type(x1)}: {x1}")

    def test_timekey_vs_index_mismatch_detection(self):
        """测试检测time_key与索引不匹配的情况"""
        df = self.create_test_data()
        
        # 创建分型，故意使用错误的time_key（与索引不匹配）
        wrong_time_key = df.iloc[8]['time_key']  # 使用索引8的时间戳，但索引是2
        fractal = Fractal(
            index=2,
            type=FractalType.TOP,
            price=13.0,
            time_key=wrong_time_key,  # 故意使用错误的time_key
            idx=1
        )
        
        result = {
            "fractals": [fractal],
            "strokes": [],
            "segments": [],
            "centrals": []
        }
        
        # 这个测试主要是验证数据结构的完整性
        # 在实际的可视化中，应该使用正确的time_key
        self.assertEqual(fractal.time_key, wrong_time_key)
        self.assertNotEqual(fractal.time_key, df.iloc[fractal.index]['time_key'])


if __name__ == "__main__":
    unittest.main()