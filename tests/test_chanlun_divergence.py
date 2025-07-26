#!/usr/bin/env python3
"""
缠论背驰判断测试套件
测试趋势背驰、盘整背驰和笔间背驰的识别功能
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chanlun_advanced_visualizer import AdvancedChanlunVisualizer
from util.chanlun import ChanlunProcessor


class TestChanlunDivergence:
    """缠论背驰测试类"""

    def __init__(self):
        self.visualizer = AdvancedChanlunVisualizer()
        self.processor = ChanlunProcessor()

    def create_divergence_test_data(self, pattern_type="trend"):
        """创建背驰测试数据"""
        if pattern_type == "trend":
            # 创建趋势背驰数据：价格创新高但MACD力度减弱
            days = 50
            base_data = {
                "time_key": pd.date_range("2024-01-01", periods=days, freq="D"),
                "open": [],
                "high": [],
                "low": [],
                "close": [],
            }

            # 模拟价格创新高但力度减弱
            for i in range(days):
                if i < 25:
                    # 第一段上涨
                    base_price = 100 + i * 0.5
                    noise = np.random.normal(0, 0.5)
                else:
                    # 第二段上涨（价格更高但斜率减小）
                    base_price = 110 + (i - 25) * 0.3
                    noise = np.random.normal(0, 0.3)

                base_data["open"].append(base_price + noise)
                base_data["high"].append(base_price + 2 + abs(noise))
                base_data["low"].append(base_price - 2 - abs(noise))
                base_data["close"].append(base_price + noise * 0.5)

            return pd.DataFrame(base_data)

        elif pattern_type == "range":
            # 创建盘整背驰数据
            days = 30
            base_data = {
                "time_key": pd.date_range("2024-01-01", periods=days, freq="D"),
                "open": [],
                "high": [],
                "low": [],
                "close": [],
            }

            # 模拟中枢震荡
            for i in range(days):
                center = 100 + np.sin(i * 0.5) * 5
                noise = np.random.normal(0, 1)

                base_data["open"].append(center + noise)
                base_data["high"].append(center + 3 + abs(noise))
                base_data["low"].append(center - 3 - abs(noise))
                base_data["close"].append(center + noise * 0.5)

            return pd.DataFrame(base_data)

        else:
            # 默认数据
            return pd.DataFrame(
                {
                    "time_key": pd.date_range("2024-01-01", periods=20, freq="D"),
                    "open": [100 + i * 0.5 for i in range(20)],
                    "high": [102 + i * 0.5 for i in range(20)],
                    "low": [98 + i * 0.5 for i in range(20)],
                    "close": [101 + i * 0.5 for i in range(20)],
                }
            )

    def test_trend_divergence(self):
        """测试趋势背驰识别"""
        print("=== 测试趋势背驰识别 ===")

        df = self.create_divergence_test_data("trend")
        result = self.processor.process(df)

        # 计算MACD
        macd_result = self.visualizer._calculate_macd(df)

        # 创建索引映射
        index_map = self.visualizer._create_index_map(df)
        merged_index_map = self.visualizer._create_merged_index_map(result)

        # 识别背驰
        divergences = self.visualizer._identify_divergences(df, result, macd_result, index_map, merged_index_map)

        # 验证趋势背驰
        trend_divergences = [d for d in divergences if "趋势" in d["type"]]
        print(f"识别到的趋势背驰数量: {len(trend_divergences)}")

        for div in trend_divergences:
            print(
                f"  类型: {div['type']}, 价格: {div['price']:.2f}, 强度: {div['strength']}"
            )

        return len(trend_divergences) > 0

    def test_range_divergence(self):
        """测试盘整背驰识别"""
        print("=== 测试盘整背驰识别 ===")

        df = self.create_divergence_test_data("range")
        result = self.processor.process(df)

        # 计算MACD
        macd_result = self.visualizer._calculate_macd(df)

        # 创建索引映射
        index_map = self.visualizer._create_index_map(df)
        merged_index_map = self.visualizer._create_merged_index_map(result)

        # 识别背驰
        divergences = self.visualizer._identify_divergences(df, result, macd_result, index_map, merged_index_map)

        # 验证盘整背驰
        range_divergences = [d for d in divergences if "盘整" in d["type"]]
        print(f"识别到的盘整背驰数量: {len(range_divergences)}")

        for div in range_divergences:
            print(
                f"  类型: {div['type']}, 价格: {div['price']:.2f}, 强度: {div['strength']}"
            )

        return len(range_divergences) > 0

    def test_stroke_divergence(self):
        """测试笔间背驰识别"""
        print("=== 测试笔间背驰识别 ===")

        df = self.create_divergence_test_data("stroke")
        result = self.processor.process(df)

        # 计算MACD
        macd_result = self.visualizer._calculate_macd(df)

        # 创建索引映射
        index_map = self.visualizer._create_index_map(df)
        merged_index_map = self.visualizer._create_merged_index_map(result)

        # 识别背驰
        divergences = self.visualizer._identify_divergences(df, result, macd_result, index_map, merged_index_map)

        # 验证笔间背驰
        stroke_divergences = [d for d in divergences if "笔间" in d["type"]]
        print(f"识别到的笔间背驰数量: {len(stroke_divergences)}")

        for div in stroke_divergences:
            print(
                f"  类型: {div['type']}, 价格: {div['price']:.2f}, 强度: {div['strength']}"
            )

        return len(stroke_divergences) > 0

    def test_macd_area_calculation(self):
        """测试MACD面积计算"""
        print("=== 测试MACD面积计算 ===")

        # 创建测试数据
        histogram = pd.Series([1, 2, 3, 2, 1, 0, -1, -2, -1, 0])

        # 计算面积
        area_dict = self.visualizer._calculate_macd_area(histogram, 0, 9)
        total_area = area_dict["red"] + area_dict["green"]
        expected_area = sum(abs(histogram))

        print(f"计算面积: {area_dict}, 总面积: {total_area}, 期望面积: {expected_area}")

        return abs(total_area - expected_area) < 0.001

    def test_edge_cases(self):
        """测试边界情况"""
        print("=== 测试边界情况 ===")

        # 空数据测试
        empty_df = pd.DataFrame(columns=["time_key", "open", "high", "low", "close"])
        result = self.processor.process(empty_df)
        macd_result = self.visualizer._calculate_macd(empty_df)
        index_map = self.visualizer._create_index_map(empty_df)
        merged_index_map = self.visualizer._create_merged_index_map(result)
        divergences = self.visualizer._identify_divergences(
            empty_df, result, macd_result, index_map, merged_index_map
        )
        print(f"空数据测试: {len(divergences)}个背驰")

        # 单根K线测试
        single_df = pd.DataFrame(
            {
                "time_key": ["2024-01-01"],
                "open": [100],
                "high": [101],
                "low": [99],
                "close": [100.5],
            }
        )
        result = self.processor.process(single_df)
        macd_result = self.visualizer._calculate_macd(single_df)
        index_map = self.visualizer._create_index_map(single_df)
        merged_index_map = self.visualizer._create_merged_index_map(result)
        divergences = self.visualizer._identify_divergences(
            single_df, result, macd_result, index_map, merged_index_map
        )
        print(f"单根K线测试: {len(divergences)}个背驰")

        # 少量K线测试
        small_df = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=5, freq="D"),
                "open": [100, 101, 102, 101, 100],
                "high": [101, 102, 103, 102, 101],
                "low": [99, 100, 101, 100, 99],
                "close": [100.5, 101.5, 102.5, 101.5, 100.5],
            }
        )
        result = self.processor.process(small_df)
        macd_result = self.visualizer._calculate_macd(small_df)
        index_map = self.visualizer._create_index_map(small_df)
        merged_index_map = self.visualizer._create_merged_index_map(result)
        divergences = self.visualizer._identify_divergences(
            small_df, result, macd_result, index_map, merged_index_map
        )
        print(f"少量K线测试: {len(divergences)}个背驰")

        return True

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行缠论背驰测试...\n")

        results = {
            "trend_divergence": self.test_trend_divergence(),
            "range_divergence": self.test_range_divergence(),
            "stroke_divergence": self.test_stroke_divergence(),
            "macd_area_calculation": self.test_macd_area_calculation(),
            "edge_cases": self.test_edge_cases(),
        }

        print("\n" + "=" * 50)
        print("📊 背驰测试总结:")
        passed = sum(results.values())
        total = len(results)
        print(f"通过: {passed}/{total}")

        for test_name, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {test_name}")

        return results


def main():
    """主测试函数"""
    tester = TestChanlunDivergence()
    results = tester.run_all_tests()

    if all(results.values()):
        print("\n🎉 所有背驰测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查实现")

    return results


if __name__ == "__main__":
    main()
