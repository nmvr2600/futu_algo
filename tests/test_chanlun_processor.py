import unittest
import pandas as pd
from util.chanlun import ChanlunProcessor, FractalType

class TestChanlunProcessor(unittest.TestCase):
    def test_kline_merge(self):
        """
        测试K线包含关系处理 - 使用清晰、明确的测试用例
        """
        # 构造测试数据:
        # K0: 基础K线 (阳)
        # K1: 被K0向上包含
        # K2: 独立K线 (阴)
        # K3: 被K2向下包含
        # K4: 被合并后的K2_3向下包含
        data = {
            'time_key': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05']),
            'open':  [10.0, 10.8, 12.0, 11.5, 10.5],
            'high':  [12.0, 11.5, 13.0, 12.0, 11.0],
            'low':   [9.0,  10.5, 10.0, 11.0, 10.0],
            'close': [11.0, 11.2, 11.0, 11.2, 10.8]
        }
        df = pd.DataFrame(data)

        # 预期合并结果:
        # 1. K0(阳) 与 K1 合并 -> 向上合并: high=max(12, 11.5)=12, low=max(9, 10.5)=10.5
        # 2. K2(阴) 与 K3 合并 -> 向下合并: high=min(13, 12)=12, low=min(10, 11)=10
        # 3. 合并后的K2_3(阴) 与 K4 合并 -> 向下合并: high=min(12, 11)=11, low=min(10, 10)=10
        expected_data = {
            'high': [12.0, 11.0],
            'low':  [10.5, 10.0]
        }
        expected_df = pd.DataFrame(expected_data)

        # 执行处理
        processor = ChanlunProcessor()
        processor._merge_k_lines(df)
        
        # 断言结果
        self.assertEqual(len(processor.merged_df), 2)
        pd.testing.assert_series_equal(processor.merged_df['high'], expected_df['high'], check_names=False)
        pd.testing.assert_series_equal(processor.merged_df['low'], expected_df['low'], check_names=False)

    def test_identify_fractals(self):
        """
        测试分型识别
        """
        # 构造测试数据 (已合并)
        # K1: 底分型, K3: 顶分型
        data = {
            'time_key': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05']),
            'high': [11, 10, 11, 13, 12],
            'low':  [9,  8,  9,  11, 11]
        }
        df = pd.DataFrame(data)

        # 预期结果
        expected_fractals = [
            Fractal(index=1, type=FractalType.BOTTOM, price=8.0),
            Fractal(index=3, type=FractalType.TOP, price=13.0)
        ]

        # 执行处理
        processor = ChanlunProcessor()
        processor.merged_df = df # 假设K线已合并
        result_fractals = processor.identify_fractals()

        # 断言结果
        self.assertEqual(len(result_fractals), 2)
        self.assertEqual(result_fractals[0].type, expected_fractals[0].type)
        self.assertEqual(result_fractals[0].price, expected_fractals[0].price)
        self.assertEqual(result_fractals[1].type, expected_fractals[1].type)
        self.assertEqual(result_fractals[1].price, expected_fractals[1].price)
