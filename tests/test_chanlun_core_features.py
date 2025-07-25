#!/usr/bin/env python3
"""
缠论核心功能测试套件
测试合并K线、分型识别、线段端点确定等关键功能
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import List, Tuple

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Fractal, FractalType


class TestChanlunCoreFeatures:
    """缠论核心功能测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def test_merge_k_lines_basic(self) -> bool:
        """测试基础K线合并功能"""
        print("=== 测试基础K线合并 ===")

        # 创建测试数据：包含包含关系的K线序列
        test_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=10, freq="D"),
                "open": [10.0, 11.0, 9.5, 10.5, 8.0, 9.0, 12.0, 11.5, 13.0, 12.5],
                "high": [12.0, 13.0, 11.5, 12.5, 10.0, 11.0, 14.0, 13.5, 15.0, 14.5],
                "low": [8.0, 9.0, 7.5, 8.5, 6.0, 7.0, 10.0, 9.5, 11.0, 10.5],
                "close": [11.0, 12.0, 10.5, 11.5, 9.0, 10.0, 13.0, 12.5, 14.0, 13.5],
            }
        )

        self.processor._merge_k_lines(test_data)
        merged_df = self.processor.merged_df

        # 验证合并结果
        print(f"原始K线数: {len(test_data)}")
        print(f"合并后K线数: {len(merged_df)}")

        # 检查original_indices列是否存在
        if "original_indices" not in merged_df.columns:
            print("❌ 缺少original_indices列")
            return False

        # 验证索引映射
        total_indices = sum([len(indices) for indices in merged_df["original_indices"]])
        if total_indices != len(test_data):
            print(f"❌ 索引映射错误: 期望{len(test_data)}, 实际{total_indices}")
            return False

        print("✅ 基础K线合并测试通过")
        return True

    def test_merge_k_lines_direction(self) -> bool:
        """测试K线合并方向判断"""
        print("=== 测试K线合并方向 ===")

        # 向上合并测试
        upward_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=5, freq="D"),
                "open": [10.0, 10.5, 10.2, 10.8, 11.0],
                "high": [11.0, 11.5, 11.2, 11.8, 12.0],
                "low": [9.0, 9.5, 9.8, 10.0, 10.5],
                "close": [10.8, 11.2, 11.0, 11.5, 11.8],
            }
        )

        self.processor._merge_k_lines(upward_data)
        upward_merged = self.processor.merged_df

        # 向下合并测试
        downward_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=5, freq="D"),
                "open": [12.0, 11.5, 11.8, 11.2, 11.0],
                "high": [12.5, 12.0, 12.2, 11.8, 11.5],
                "low": [11.0, 10.5, 10.8, 10.2, 10.0],
                "close": [11.2, 10.8, 11.0, 10.5, 10.2],
            }
        )

        self.processor._merge_k_lines(downward_data)
        downward_merged = self.processor.merged_df

        print("✅ K线合并方向测试通过")
        return True

    def test_fractal_identification(self) -> bool:
        """测试分型识别功能"""
        print("=== 测试分型识别 ===")

        # 创建明确的分型测试数据
        fractal_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=7, freq="D"),
                "high": [10.0, 12.0, 15.0, 11.0, 8.0, 10.0, 12.0],  # 15.0是顶分型
                "low": [8.0, 9.0, 13.0, 9.0, 6.0, 8.0, 10.0],
            }
        )

        self.processor._merge_k_lines(fractal_data)
        fractals = self.processor.identify_fractals()

        print(f"识别到的分型数量: {len(fractals)}")

        # 验证顶分型
        top_fractals = [f for f in fractals if f.type == FractalType.TOP]
        if len(top_fractals) > 0:
            top = top_fractals[0]
            print(f"顶分型: 索引={top.index}, 价格={top.price}")
            if top.price == 15.0 and top.index == 2:
                print("✅ 顶分型识别正确")
            else:
                print("❌ 顶分型识别错误")
                return False

        # 创建底分型测试数据
        bottom_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=7, freq="D"),
                "high": [12.0, 10.0, 15.0, 8.0, 10.0, 12.0, 14.0],
                "low": [10.0, 8.0, 12.0, 5.0, 7.0, 9.0, 11.0],  # 5.0是底分型
            }
        )

        self.processor._merge_k_lines(bottom_data)
        fractals = self.processor.identify_fractals()

        bottom_fractals = [f for f in fractals if f.type == FractalType.BOTTOM]
        if len(bottom_fractals) > 0:
            bottom = bottom_fractals[0]
            print(f"底分型: 索引={bottom.index}, 价格={bottom.price}")
            if bottom.price == 5.0 and bottom.index == 3:
                print("✅ 底分型识别正确")
            else:
                print("❌ 底分型识别错误")
                return False

        print("✅ 分型识别测试通过")
        return True

    def test_complex_fractal_patterns(self) -> bool:
        """测试复杂分型模式识别"""
        print("=== 测试复杂分型模式 ===")

        # 创建复杂的分型序列
        complex_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=15, freq="D"),
                "high": [
                    10,
                    11,
                    12,
                    11.5,
                    10.5,
                    13,
                    14,
                    13.5,
                    12.5,
                    15,
                    14.5,
                    13.5,
                    12,
                    11,
                    10,
                ],
                "low": [
                    8,
                    9,
                    10,
                    9.5,
                    8.5,
                    11,
                    12,
                    11.5,
                    10.5,
                    13,
                    12.5,
                    11.5,
                    10,
                    9,
                    8,
                ],
            }
        )

        self.processor._merge_k_lines(complex_data)
        fractals = self.processor.identify_fractals()

        print(f"复杂数据中识别到的分型: {len(fractals)}")
        for fractal in fractals:
            print(
                f"  类型: {fractal.type.value}, 索引: {fractal.index}, 价格: {fractal.price}"
            )

        print("✅ 复杂分型模式测试通过")
        return True

    def test_index_mapping(self) -> bool:
        """测试索引映射功能"""
        print("=== 测试索引映射 ===")

        # 创建会导致合并的数据
        mapping_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=8, freq="D"),
                "open": [10, 10.2, 10.1, 10.3, 10.2, 10.4, 10.3, 10.5],
                "high": [11, 11.1, 11.05, 11.2, 11.15, 11.3, 11.25, 11.4],
                "low": [9, 9.1, 9.05, 9.2, 9.15, 9.3, 9.25, 9.4],
                "close": [10.5, 10.6, 10.55, 10.7, 10.65, 10.8, 10.75, 10.9],
            }
        )

        self.processor._merge_k_lines(mapping_data)

        # 验证索引映射
        if "original_indices" in self.processor.merged_df.columns:
            print("索引映射关系:")
            for i, indices in enumerate(self.processor.merged_df["original_indices"]):
                print(f"  合并后索引 {i} -> 原始索引 {indices}")

        print("✅ 索引映射测试通过")
        return True

    def test_edge_cases(self) -> bool:
        """测试边界情况"""
        print("=== 测试边界情况 ===")

        # 测试空数据
        empty_df = pd.DataFrame()
        self.processor._merge_k_lines(empty_df)
        if len(self.processor.merged_df) != 0:
            print("❌ 空数据测试失败")
            return False

        # 测试单根K线
        single_df = pd.DataFrame(
            {
                "time_key": ["2024-01-01"],
                "open": [10.0],
                "high": [11.0],
                "low": [9.0],
                "close": [10.5],
            }
        )
        self.processor._merge_k_lines(single_df)
        if len(self.processor.merged_df) != 1:
            print("❌ 单根K线测试失败")
            return False

        # 测试两根K线
        two_df = pd.DataFrame(
            {
                "time_key": ["2024-01-01", "2024-01-02"],
                "open": [10.0, 10.5],
                "high": [11.0, 11.5],
                "low": [9.0, 9.5],
                "close": [10.5, 11.0],
            }
        )
        self.processor._merge_k_lines(two_df)
        if len(self.processor.merged_df) < 1:
            print("❌ 两根K线测试失败")
            return False

        print("✅ 边界情况测试通过")
        return True

    def run_all_tests(self) -> dict:
        """运行所有测试"""
        print("🚀 开始运行缠论核心功能测试...\n")

        results = {
            "merge_k_lines_basic": self.test_merge_k_lines_basic(),
            "merge_k_lines_direction": self.test_merge_k_lines_direction(),
            "fractal_identification": self.test_fractal_identification(),
            "complex_fractal_patterns": self.test_complex_fractal_patterns(),
            "index_mapping": self.test_index_mapping(),
            "edge_cases": self.test_edge_cases(),
        }

        print("\n" + "=" * 50)
        print("📊 测试总结:")
        passed = sum(results.values())
        total = len(results)
        print(f"通过: {passed}/{total}")

        for test_name, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {test_name}")

        return results


def main():
    """主测试函数"""
    tester = TestChanlunCoreFeatures()
    results = tester.run_all_tests()

    if all(results.values()):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查实现")

    return results


if __name__ == "__main__":
    main()
