#!/usr/bin/env python3
"""
验证time_key在可视化中的正确使用
"""

import pandas as pd
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


class TestTimeKeyVisualizationValidation(unittest.TestCase):
    """验证time_key在可视化中的正确使用"""

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

    def test_fractals_use_timekey_directly(self):
        """测试分型直接使用time_key而非索引"""
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

    def test_strokes_use_timekey_directly(self):
        """测试笔直接使用time_key而非索引"""
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

    def test_centrals_use_timekey_directly(self):
        """测试中枢直接使用time_key而非索引"""
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


if __name__ == "__main__":
    unittest.main()