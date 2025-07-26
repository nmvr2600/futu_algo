import unittest
import pandas as pd
from util.chanlun import ChanlunProcessor, FractalType, Fractal, Stroke, Central


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
            "time_key": pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
            ),
            "open": [10.0, 10.8, 12.0, 11.5, 10.5],
            "high": [12.0, 11.5, 13.0, 12.0, 11.0],
            "low": [9.0, 10.5, 10.0, 11.0, 10.0],
            "close": [11.0, 11.2, 11.0, 11.2, 10.8],
        }
        df = pd.DataFrame(data)

        # 预期合并结果:
        # 1. K0(阳) 与 K1 合并 -> 向上合并: high=max(12, 11.5)=12, low=max(9, 10.5)=10.5
        # 2. K2(阴) 与 K3 合并 -> 向下合并: high=min(13, 12)=12, low=min(10, 11)=10
        expected_data = {"high": [13.0, 11.0], "low": [11.0, 10.0]}
        expected_df = pd.DataFrame(expected_data)

        # 执行处理
        processor = ChanlunProcessor()
        processor._merge_k_lines(df)

        # 断言结果
        self.assertIsNotNone(processor.merged_df)
        self.assertEqual(len(processor.merged_df), 2)  # type: ignore
        pd.testing.assert_series_equal(
            processor.merged_df["high"], expected_df["high"], check_names=False  # type: ignore
        )
        pd.testing.assert_series_equal(
            processor.merged_df["low"], expected_df["low"], check_names=False  # type: ignore
        )

    def test_identify_fractals(self):
        """
        测试分型识别
        """
        # 构造测试数据 (已合并)
        # K0: 顶分型, K2: 底分型
        data = {
            "time_key": pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
            ),
            "high": [11, 12, 10, 11, 12],
            "low": [9, 10, 8, 9, 10],
        }
        df = pd.DataFrame(data)

        # 预期结果
        expected_fractals = [
            Fractal(index=1, type=FractalType.TOP, price=12.0, idx=1),
            Fractal(index=2, type=FractalType.BOTTOM, price=8.0, idx=2),
        ]

        # 执行处理
        processor = ChanlunProcessor()
        processor.merged_df = df  # 假设K线已合并
        result_fractals = processor.identify_fractals()

        # 断言结果
        self.assertEqual(len(result_fractals), 2)
        self.assertEqual(result_fractals[0].type, expected_fractals[0].type)
        self.assertEqual(result_fractals[0].price, expected_fractals[0].price)
        self.assertEqual(result_fractals[1].type, expected_fractals[1].type)
        self.assertEqual(result_fractals[1].price, expected_fractals[1].price)

    def test_index_mapping(self):
        """
        测试索引映射功能
        """
        # 创建测试数据
        data = {
            "time_key": pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
            ),
            "open": [10.0, 10.8, 12.0, 11.5, 10.5],
            "high": [12.0, 11.5, 13.0, 12.0, 11.0],
            "low": [9.0, 10.5, 10.0, 11.0, 10.0],
            "close": [11.0, 11.2, 11.0, 11.2, 10.8],
        }
        df = pd.DataFrame(data)

        # 执行处理
        processor = ChanlunProcessor()
        result = processor.process(df)

        # 验证索引映射存在且正确
        self.assertIn("index_mapping", result)
        self.assertIsInstance(result["index_mapping"], dict)
        self.assertEqual(len(result["index_mapping"]), 2)  # 应该有2个合并后的索引

        # 验证映射关系
        expected_mapping = {0: [0, 1, 2, 3], 1: [4]}
        self.assertEqual(result["index_mapping"], expected_mapping)

    def test_visualization_coordinates(self):
        """
        测试可视化坐标处理
        """
        # 创建测试数据
        data = {
            "time_key": pd.date_range("2025-01-01", periods=10, freq="D"),
            "open": [10.0, 10.5, 11.0, 10.8, 10.2, 10.7, 11.2, 11.0, 10.5, 10.8],
            "high": [11.0, 11.5, 12.0, 11.8, 11.2, 11.7, 12.2, 12.0, 11.5, 11.8],
            "low": [9.0, 9.5, 10.0, 9.8, 9.2, 9.7, 10.2, 10.0, 9.5, 9.8],
            "close": [10.5, 11.0, 11.5, 11.2, 10.7, 11.1, 11.8, 11.5, 11.0, 11.2],
        }
        df = pd.DataFrame(data)

        # 执行处理
        processor = ChanlunProcessor()
        result = processor.process(df)

        # 验证所有结果都有正确的索引
        self.assertIsInstance(result["merged_df"], pd.DataFrame)
        self.assertIsInstance(result["fractals"], list)
        self.assertIsInstance(result["strokes"], list)

        # 验证分型索引在合并数据范围内
        for fractal in result["fractals"]:
            self.assertGreaterEqual(fractal.index, 0)
            self.assertLess(fractal.index, len(result["merged_df"]))

        # 验证笔索引在合并数据范围内
        for stroke in result["strokes"]:
            self.assertGreaterEqual(stroke.start_index, 0)
            self.assertLess(stroke.start_index, len(result["merged_df"]))
            self.assertGreaterEqual(stroke.end_index, 0)
            self.assertLess(stroke.end_index, len(result["merged_df"]))

        # 验证索引映射的完整性
        total_original_indices = sum(
            len(indices) for indices in result["index_mapping"].values()
        )
        self.assertEqual(total_original_indices, len(df))


if __name__ == "__main__":
    unittest.main()
