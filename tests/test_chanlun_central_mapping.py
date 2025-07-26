#!/usr/bin/env python3
"""
缠论中枢和索引映射测试套件
测试中枢识别和索引映射功能
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import List, Tuple, Dict

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Central, Fractal, FractalType


class TestChanlunCentralMapping:
    """缠论中枢和索引映射测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_central_test_data(self) -> pd.DataFrame:
        """创建中枢测试数据"""
        # 创建包含明显中枢结构的数据
        days = 25
        data = {
            "time_key": pd.date_range("2024-01-01", periods=days, freq="D"),
            "open": [
                10.0,
                11.0,
                12.0,
                11.0,
                10.0,
                9.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                11.0,
                10.0,
                9.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                11.0,
                10.0,
                9.0,
                8.0,
                9.0,
                10.0,
            ],
            "high": [
                11.0,
                12.0,
                13.0,
                12.0,
                11.0,
                10.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0,
                12.0,
                11.0,
                10.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0,
                12.0,
                11.0,
                10.0,
                9.0,
                10.0,
                11.0,
            ],
            "low": [
                9.0,
                10.0,
                11.0,
                10.0,
                9.0,
                8.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                10.0,
                9.0,
                8.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                10.0,
                9.0,
                8.0,
                7.0,
                8.0,
                9.0,
            ],
            "close": [
                10.5,
                11.5,
                12.5,
                11.5,
                10.5,
                9.5,
                8.5,
                9.5,
                10.5,
                11.5,
                12.5,
                11.5,
                10.5,
                9.5,
                8.5,
                9.5,
                10.5,
                11.5,
                12.5,
                11.5,
                10.5,
                9.5,
                8.5,
                9.5,
                10.5,
            ],
        }
        return pd.DataFrame(data)

    def test_central_identification(self) -> bool:
        """测试中枢识别"""
        print("=== 测试中枢识别 ===")

        df = self.create_central_test_data()

        # 执行完整的缠论处理
        self.processor._merge_k_lines(df)
        fractals = self.processor.identify_fractals()
        strokes = self.processor.build_strokes()
        centrals = self.processor.build_centrals()

        print(f"分型: {len(fractals)}, 笔: {len(strokes)}, 中枢: {len(centrals)}")

        # 验证中枢基本属性
        for central in centrals:
            print(
                f"中枢: 起点={central.start_index}, 终点={central.end_index}, "
                f"高点={central.high:.2f}, 低点={central.low:.2f}"
            )

            # 验证中枢范围
            if central.start_index < 0 or central.end_index >= len(df):
                print(f"❌ 中枢索引越界")
                return False

            if central.high <= central.low:
                print(f"❌ 中枢价格范围无效: 高={central.high}, 低={central.low}")
                return False

        print("✅ 中枢识别测试通过")
        return True

    def test_central_overlap_condition(self) -> bool:
        """测试中枢重叠条件"""
        print("=== 测试中枢重叠条件 ===")

        df = self.create_central_test_data()
        self.processor._merge_k_lines(df)
        self.processor.identify_fractals()
        self.processor.build_strokes()
        centrals = self.processor.build_centrals()

        # 验证中枢重叠
        for central in centrals:
            if len(central.strokes) >= 3:
                # 检查笔之间是否有重叠
                stroke_prices = []
                for stroke in central.strokes:
                    stroke_prices.extend([stroke.start_price, stroke.end_price])

                min_price = min(stroke_prices)
                max_price = max(stroke_prices)

                # 验证中枢范围包含所有笔的价格
                if central.low > min_price or central.high < max_price:
                    print(f"❌ 中枢范围不包含所有笔的价格")
                    return False

        print("✅ 中枢重叠条件测试通过")
        return True

    def test_index_mapping_consistency(self) -> bool:
        """测试索引映射一致性"""
        print("=== 测试索引映射一致性 ===")

        df = self.create_central_test_data()

        # 获取合并后的数据
        self.processor._merge_k_lines(df)
        merged_df = self.processor.merged_df

        if merged_df is None or merged_df.empty:
            print("❌ 合并数据为空")
            return False

        print(f"原始数据长度: {len(df)}")
        print(f"合并后数据长度: {len(merged_df)}")

        # 验证索引映射
        if "original_indices" in merged_df.columns:
            # 计算映射的完整性
            total_mapped = 0
            for indices in merged_df["original_indices"]:
                total_mapped += len(indices)

            print(f"索引映射统计: 原始{len(df)} -> 映射{total_mapped}")

            if total_mapped != len(df):
                print("❌ 索引映射不完整")
                return False

        print("✅ 索引映射一致性测试通过")
        return True

    def test_central_stroke_correlation(self) -> bool:
        """测试中枢与笔的关联"""
        print("=== 测试中枢与笔关联 ===")

        df = self.create_central_test_data()
        self.processor._merge_k_lines(df)
        self.processor.identify_fractals()
        self.processor.build_strokes()
        centrals = self.processor.build_centrals()

        for central in centrals:
            # 验证中枢包含的笔数量
            if len(central.strokes) < 3:
                print(f"❌ 中枢笔数不足: {len(central.strokes)} < 3")
                return False

            # 验证笔的时间顺序
            for i in range(1, len(central.strokes)):
                prev_stroke = central.strokes[i - 1]
                curr_stroke = central.strokes[i]

                if prev_stroke.end_index > curr_stroke.start_index:
                    print("❌ 中枢内笔时间顺序错误")
                    return False

        print("✅ 中枢与笔关联测试通过")
        return True

    def test_fractal_index_mapping(self) -> bool:
        """测试分型索引映射"""
        print("=== 测试分型索引映射 ===")

        df = self.create_central_test_data()
        self.processor._merge_k_lines(df)
        fractals = self.processor.identify_fractals()

        # 获取合并后的数据
        merged_df = self.processor.merged_df

        if merged_df is None:
            print("❌ 合并数据为空")
            return False

        print(f"分型数量: {len(fractals)}")
        print(f"合并后数据长度: {len(merged_df)}")

        # 验证分型索引在合并后数据范围内
        for fractal in fractals:
            if fractal.index < 0 or fractal.index >= len(merged_df):
                print(f"❌ 分型索引越界: {fractal.index} 不在 [0, {len(merged_df)})")
                return False

            # 验证分型价格与合并后数据匹配
            if fractal.type == FractalType.TOP:
                expected_price = merged_df.iloc[fractal.index]["high"]
            else:
                expected_price = merged_df.iloc[fractal.index]["low"]

            if abs(fractal.price - expected_price) > 0.01:
                print(f"❌ 分型价格不匹配: 期望{expected_price}, 实际{fractal.price}")
                return False

        print("✅ 分型索引映射测试通过")
        return True

    def test_visualization_index_mapping(self) -> bool:
        """测试可视化索引映射"""
        print("=== 测试可视化索引映射 ===")

        df = self.create_central_test_data()

        # 获取合并后的数据
        self.processor._merge_k_lines(df)
        merged_df = self.processor.merged_df

        if merged_df is None or merged_df.empty:
            print("❌ 合并数据为空")
            return False

        # 创建索引映射
        original_to_merged_map = {}
        if "original_indices" in merged_df.columns:
            for merged_idx, row in merged_df.iterrows():
                original_indices = row["original_indices"]
                for orig_idx in original_indices:
                    original_to_merged_map[orig_idx] = merged_idx

        print(f"索引映射条目: {len(original_to_merged_map)}")
        print(f"预期映射: {len(df)} -> {len(merged_df)}")

        # 验证映射的完整性
        for orig_idx in range(len(df)):
            if orig_idx not in original_to_merged_map:
                print(f"❌ 缺失索引映射: {orig_idx}")
                return False

        print("✅ 可视化索引映射测试通过")
        return True

    def test_central_boundaries(self) -> bool:
        """测试中枢边界条件"""
        print("=== 测试中枢边界条件 ===")

        # 创建边界测试数据
        boundary_data = {
            "time_key": pd.date_range("2024-01-01", periods=10, freq="D"),
            "open": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            "high": [11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0],
            "low": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
            "close": [10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5],
        }
        df = pd.DataFrame(boundary_data)

        self.processor._merge_k_lines(df)
        self.processor.identify_fractals()
        self.processor.build_strokes()
        centrals = self.processor.build_centrals()

        # 边界情况验证
        if len(centrals) > 0:
            central = centrals[0]
            print(f"边界中枢: 高点={central.high}, 低点={central.low}")

            if central.high == central.low:
                print("⚠️  中枢价格范围为零")

        print("✅ 中枢边界条件测试通过")
        return True

    def test_complex_central_patterns(self) -> bool:
        """测试复杂中枢模式"""
        print("=== 测试复杂中枢模式 ===")

        # 创建复杂中枢数据
        complex_data = {
            "time_key": pd.date_range("2024-01-01", periods=50, freq="D"),
            "open": [],
            "high": [],
            "low": [],
            "close": [],
        }

        # 模拟复杂震荡走势
        for i in range(50):
            base = 10 + (i % 10) * 0.1
            complex_data["open"].append(base)
            complex_data["high"].append(base + 1.0)
            complex_data["low"].append(base - 1.0)
            complex_data["close"].append(base + 0.5)

        df = pd.DataFrame(complex_data)

        self.processor._merge_k_lines(df)
        self.processor.identify_fractals()
        self.processor.build_strokes()
        centrals = self.processor.build_centrals()

        print(f"复杂数据中识别出的中枢: {len(centrals)}")

        # 验证中枢的合理性
        for central in centrals:
            if central.end_index - central.start_index < 2:
                print("❌ 中枢区间过小")
                return False

        print("✅ 复杂中枢模式测试通过")
        return True

    def run_all_tests(self) -> dict:
        """运行所有测试"""
        print("🚀 开始运行缠论中枢和索引映射测试...\n")

        results = {
            "central_identification": self.test_central_identification(),
            "central_overlap_condition": self.test_central_overlap_condition(),
            "index_mapping_consistency": self.test_index_mapping_consistency(),
            "central_stroke_correlation": self.test_central_stroke_correlation(),
            "fractal_index_mapping": self.test_fractal_index_mapping(),
            "visualization_index_mapping": self.test_visualization_index_mapping(),
            "central_boundaries": self.test_central_boundaries(),
            "complex_central_patterns": self.test_complex_central_patterns(),
        }

        print("\n" + "=" * 60)
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
    tester = TestChanlunCentralMapping()
    results = tester.run_all_tests()

    if all(results.values()):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查实现")

    return results


if __name__ == "__main__":
    main()
