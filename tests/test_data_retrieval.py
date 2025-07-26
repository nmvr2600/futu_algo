#!/usr/bin/env python3
"""
测试数据获取功能
"""

import pandas as pd
import sys
import os
import unittest

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom.chanlun_selector_demo import get_stock_data


class TestDataRetrieval(unittest.TestCase):
    """测试数据获取功能"""

    def test_valid_stock_data_retrieval(self):
        """测试有效股票数据获取"""
        # 测试腾讯股票数据获取
        symbol = "0700.HK"
        data = get_stock_data(symbol, period="1mo", interval="1d")
        
        # 验证返回的数据不是空的
        self.assertFalse(data.empty, f"无法获取 {symbol} 的数据")
        
        # 验证数据包含必要的列
        expected_columns = ['open', 'high', 'low', 'close', 'volume', 'time_key']
        for col in expected_columns:
            self.assertIn(col, data.columns, f"缺少必要的列: {col}")
        
        # 验证time_key列存在且为datetime类型
        self.assertIn('time_key', data.columns, "缺少time_key列")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(data['time_key']), 
                       "time_key列应该为datetime类型")
        
        # 验证数据行数合理
        self.assertGreater(len(data), 0, "数据行数应该大于0")
        
        print(f"成功获取 {symbol} 的数据，共 {len(data)} 行")
        print(f"数据列: {list(data.columns)}")
        if not data.empty:
            print(f"时间范围: {data['time_key'].min()} 到 {data['time_key'].max()}")

    def test_invalid_stock_data_retrieval(self):
        """测试无效股票数据获取"""
        # 测试一个可能不存在的股票代码
        symbol = "03888.HK"  # 可能已退市的股票
        data = get_stock_data(symbol, period="1mo", interval="1d")
        
        # 验证返回空数据
        self.assertTrue(data.empty, f"应该无法获取 {symbol} 的数据，但返回了数据")
        print(f"正确处理了无效股票代码 {symbol}，返回空数据")

    def test_different_intervals(self):
        """测试不同时间间隔的数据获取"""
        symbol = "0700.HK"
        
        # 测试日线数据
        daily_data = get_stock_data(symbol, period="1mo", interval="1d")
        self.assertFalse(daily_data.empty, "无法获取日线数据")
        print(f"日线数据: {len(daily_data)} 行")
        
        # 测试15分钟数据
        min15_data = get_stock_data(symbol, period="1mo", interval="15m")
        self.assertFalse(min15_data.empty, "无法获取15分钟数据")
        print(f"15分钟数据: {len(min15_data)} 行")
        
        # 验证两种时间间隔的数据量不同
        self.assertNotEqual(len(daily_data), len(min15_data), 
                           "不同时间间隔应该返回不同数量的数据")

    def test_data_structure(self):
        """测试数据结构完整性"""
        symbol = "0700.HK"
        data = get_stock_data(symbol, period="1mo", interval="1d")
        
        # 验证数据不为空
        self.assertFalse(data.empty)
        
        # 验证所有必要的列都存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            self.assertIn(col, data.columns)
            # 验证数值列的数据类型
            self.assertTrue(pd.api.types.is_numeric_dtype(data[col]), 
                           f"{col} 列应该是数值类型")
        
        # 验证时间列
        self.assertIn('time_key', data.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(data['time_key']))
        
        # 验证数据一致性
        if len(data) > 0:
            # 验证价格列的合理性
            self.assertTrue((data['high'] >= data['low']).all(), 
                           "最高价应该大于等于最低价")
            self.assertTrue((data['high'] >= data['open']).all() | 
                           (data['high'] >= data['close']).all(),
                           "最高价应该大于等于开盘价或收盘价")
            self.assertTrue((data['low'] <= data['open']).all() | 
                           (data['low'] <= data['close']).all(),
                           "最低价应该小于等于开盘价或收盘价")


if __name__ == "__main__":
    unittest.main()