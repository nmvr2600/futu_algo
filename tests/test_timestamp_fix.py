#!/usr/bin/env python3
"""
时间戳修复功能测试
测试get_stock_data函数中时间戳处理的正确性，确保不会出现1970年显示问题
"""

import pandas as pd
import sys
import os
from unittest.mock import Mock, patch

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTimestampFix:
    """时间戳修复测试类"""
    
    def __init__(self):
        # 导入需要测试的函数
        custom_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'custom')
        if custom_path not in sys.path:
            sys.path.append(custom_path)
        from chanlun_selector_demo import get_stock_data
        self.get_stock_data = get_stock_data
    
    def test_get_stock_data_timestamp_type(self):
        """测试get_stock_data函数返回的时间戳类型是否为datetime"""
        print("=== 测试get_stock_data时间戳类型 ===")
        
        # 创建模拟的yfinance数据
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [101.0, 102.0, 103.0],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2024-01-01', periods=3, freq='D'))
        
        # 使用patch模拟yfinance.Ticker().history()的返回值
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker_instance = Mock()
            mock_ticker_instance.history.return_value = mock_data
            mock_ticker.return_value = mock_ticker_instance
            
            # 调用函数
            result = self.get_stock_data('TEST.STOCK')
            
            # 验证结果不为空
            assert not result.empty, "返回的数据框不应为空"
            
            # 验证time_key列存在
            assert 'time_key' in result.columns, "应包含time_key列"
            
            # 验证time_key列的类型为datetime
            assert pd.api.types.is_datetime64_any_dtype(result['time_key']), \
                f"time_key列应为datetime类型，实际类型为{result['time_key'].dtype}"
            
            # 验证time_key值正确
            expected_dates = pd.date_range('2024-01-01', periods=3, freq='D')
            for i, expected_date in enumerate(expected_dates):
                actual_date = result.iloc[i]['time_key']
                assert actual_date == expected_date, \
                    f"时间戳不匹配: 期望{expected_date}, 实际{actual_date}"
            
            print("✅ get_stock_data时间戳类型测试通过")
            return True
    
    def test_get_stock_data_with_empty_data(self):
        """测试get_stock_data函数处理空数据的情况"""
        print("=== 测试get_stock_data处理空数据 ===")
        
        # 使用patch模拟yfinance.Ticker().history()返回空数据
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker_instance = Mock()
            mock_ticker_instance.history.return_value = pd.DataFrame()
            mock_ticker.return_value = mock_ticker_instance
            
            # 调用函数
            result = self.get_stock_data('EMPTY.STOCK')
            
            # 验证返回空DataFrame
            assert isinstance(result, pd.DataFrame), "应返回DataFrame"
            assert result.empty, "应返回空DataFrame"
            
            print("✅ get_stock_data空数据处理测试通过")
            return True
    
    def test_get_stock_data_exception_handling(self):
        """测试get_stock_data函数异常处理"""
        print("=== 测试get_stock_data异常处理 ===")
        
        # 使用patch模拟yfinance.Ticker()抛出异常
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.side_effect = Exception("网络错误")
            
            # 调用函数
            result = self.get_stock_data('ERROR.STOCK')
            
            # 验证返回空DataFrame
            assert isinstance(result, pd.DataFrame), "应返回DataFrame"
            assert result.empty, "异常时应返回空DataFrame"
            
            print("✅ get_stock_data异常处理测试通过")
            return True


def run_tests():
    """运行所有测试"""
    print("开始运行时间戳修复测试...")
    
    test_instance = TestTimestampFix()
    
    tests = [
        test_instance.test_get_stock_data_timestamp_type,
        test_instance.test_get_stock_data_with_empty_data,
        test_instance.test_get_stock_data_exception_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 {test.__name__} 失败: {e}")
            failed += 1
    
    print(f"\n测试完成: {passed} 通过, {failed} 失败")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)