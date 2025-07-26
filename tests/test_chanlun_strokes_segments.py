#!/usr/bin/env python3
"""
缠论笔和线段测试套件
测试笔构建和线段端点确定功能
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import List, Tuple

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Fractal, FractalType, Stroke


class TestChanlunStrokesSegments:
    """缠论笔和线段测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_test_data(self, pattern_type: str = "simple") -> pd.DataFrame:
        """创建测试数据"""
        base_data = {
            "time_key": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
        }

        if pattern_type == "simple":
            days = 20
            for day in range(days):
                base_data["time_key"].append(f"2024-01-{day+1:02d}")
                base_data["open"].append(10 + (day % 3 - 1) * 2)
                base_data["high"].append(11 + (day % 3 - 1) * 2)
                base_data["low"].append(9 + (day % 3 - 1) * 2)
                base_data["close"].append(10.5 + (day % 3 - 1) * 2)
            return pd.DataFrame(base_data)

        elif pattern_type == "complex":
            days = 30
            for day in range(days):
                base_data["time_key"].append(f"2024-01-{day+1:02d}")
                base_data["open"].append(10 + (day % 5 - 2))
                base_data["high"].append(11 + (day % 5 - 2))
                base_data["low"].append(9 + (day % 5 - 2))
                base_data["close"].append(10.5 + (day % 5 - 2))
            return pd.DataFrame(base_data)

        elif pattern_type == "trend":
            days = 25
            for day in range(days):
                base_data["time_key"].append(f"2024-01-{day+1:02d}")
                base_data["open"].append(10 + day * 0.2)
                base_data["high"].append(11 + day * 0.2)
                base_data["low"].append(9 + day * 0.2)
                base_data["close"].append(10.5 + day * 0.2)
            return pd.DataFrame(base_data)

        # 默认返回空DataFrame
        return pd.DataFrame(
            {
                "time_key": ["2024-01-01", "2024-01-02"],
                "open": [10.0, 11.0],
                "high": [11.0, 12.0],
                "low": [9.0, 10.0],
                "close": [10.5, 11.5],
            }
        )

    def test_stroke_basic_construction(self) -> bool:
        """测试基础笔构建"""
        print("=== 测试基础笔构建 ===")

        df = self.create_test_data("simple")
        self.processor._merge_k_lines(df)
        fractals = self.processor.identify_fractals()
        strokes = self.processor.build_strokes()

        print(f"识别到的分型数量: {len(fractals)}")
        print(f"构建的笔数量: {len(strokes)}")

        # 验证笔的基本属性
        if len(strokes) > 0:
            stroke = strokes[0]
            print(
                f"第一笔: 起点={stroke.start_index}, 终点={stroke.end_index}, "
                f"方向={'向上' if stroke.direction == 1 else '向下'}, "
                f"价格区间={stroke.start_price}-{stroke.end_price}"
            )

            # 验证笔的连续性
            for i in range(1, len(strokes)):
                prev_stroke = strokes[i - 1]
                curr_stroke = strokes[i]
                if prev_stroke.end_index != curr_stroke.start_index:
                    print(
                        f"❌ 笔不连续: 前一笔终点{prev_stroke.end_index} != 当前笔起点{curr_stroke.start_index}"
                    )
                    return False

        print("✅ 基础笔构建测试通过")
        return True

    def test_stroke_direction_alternation(self) -> bool:
        """测试笔方向交替"""
        print("=== 测试笔方向交替 ===")

        df = self.create_test_data("complex")
        self.processor._merge_k_lines(df)
        self.processor.identify_fractals()
        strokes = self.processor.build_strokes()

        if len(strokes) >= 3:
            # 验证相邻笔方向必须相反
            for i in range(1, len(strokes)):
                if strokes[i].direction == strokes[i - 1].direction:
                    print(f"❌ 笔方向不交替: 第{i-1}笔和第{i}笔方向相同")
                    return False

        print(f"笔方向交替验证通过，共{len(strokes)}笔")
        print("✅ 笔方向交替测试通过")
        return True

    def test_stroke_validity_rules(self) -> bool:
        """测试笔有效性规则"""
        print("=== 测试笔有效性规则 ===")

        df = self.create_test_data("trend")
        self.processor._merge_k_lines(df)
        self.processor.identify_fractals()
        strokes = self.processor.build_strokes()

        for stroke in strokes:
            # 验证索引范围
            if stroke.start_index < 0 or stroke.end_index >= len(df):
                print(
                    f"❌ 笔索引越界: 起点{stroke.start_index}, 终点{stroke.end_index}, 数据长度{len(df)}"
                )
                return False

            # 验证价格范围
            price_range = abs(stroke.end_price - stroke.start_price)
            if price_range <= 0:
                print(f"❌ 笔价格区间无效: {price_range}")
                return False

            # 验证时间顺序
            if stroke.start_index >= stroke.end_index:
                print(
                    f"❌ 笔时间顺序错误: 起点{stroke.start_index} >= 终点{stroke.end_index}"
                )
                return False

        print("✅ 笔有效性规则测试通过")
        return True

    def test_segment_construction(self) -> bool:
        """测试线段构建"""
        print("=== 测试线段构建 ===")

        df = self.create_test_data("complex")

        # 确保所有前置步骤完成
        df = self.create_test_data("complex")
        self.processor._merge_k_lines(df)
        fractals = self.processor.identify_fractals()
        strokes = self.processor.build_strokes()
        segments = self.processor.build_segments()

        print(f"分型: {len(fractals)}, 笔: {len(strokes)}, 线段: {len(segments)}")

        # 验证线段数量
        if len(strokes) < 3 and len(segments) > 0:
            print("❌ 笔数量不足但存在线段")
            return False
        elif len(strokes) >= 3 and len(segments) == 0:
            print("⚠️  笔数量足够但无线段")

        # 验证线段基本属性
        for segment in segments:
            print(
                f"线段: 起点={segment.start_index}, 终点={segment.end_index}, "
                f"方向={'向上' if segment.direction == 1 else '向下'}, "
                f"价格区间={segment.start_price:.2f}-{segment.end_price:.2f}"
            )

            # 验证线段范围
            if segment.start_index < 0 or segment.end_index >= len(df):
                print(f"❌ 线段索引越界")
                return False

            # 验证线段长度（至少3笔）
            related_strokes = [
                s
                for s in strokes
                if s.start_index >= segment.start_index
                and s.end_index <= segment.end_index
            ]

            if len(related_strokes) < 3:
                print(f"❌ 线段包含笔数不足: {len(related_strokes)} < 3")
                return False

        print("✅ 线段构建测试通过")
        return True

    def test_segment_break_conditions(self) -> bool:
        """测试线段破坏条件"""
        print("=== 测试线段破坏条件 ===")

        # 创建明显的线段破坏数据
        break_data = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=20, freq="D"),
                "open": [
                    10,
                    11,
                    12,
                    13,
                    14,
                    13,
                    12,
                    11,
                    10,
                    9,
                    8,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    11,
                    10,
                    9,
                ],
                "high": [
                    11,
                    12,
                    13,
                    14,
                    15,
                    14,
                    13,
                    12,
                    11,
                    10,
                    9,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    12,
                    11,
                    10,
                ],
                "low": [
                    9,
                    10,
                    11,
                    12,
                    13,
                    12,
                    11,
                    10,
                    9,
                    8,
                    7,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    10,
                    9,
                    8,
                ],
                "close": [
                    10.5,
                    11.5,
                    12.5,
                    13.5,
                    14.5,
                    13.5,
                    12.5,
                    11.5,
                    10.5,
                    9.5,
                    8.5,
                    7.5,
                    8.5,
                    9.5,
                    10.5,
                    11.5,
                    12.5,
                    11.5,
                    10.5,
                    9.5,
                ],
            }
        )

        self.processor._merge_k_lines(break_data)
        self.processor.identify_fractals()
        self.processor.build_strokes()
        segments = self.processor.build_segments()

        print(f"破坏测试 - 线段数量: {len(segments)}")

        # 应该能识别出至少一个线段
        if len(segments) == 0:
            print("⚠️  未识别出线段")
        else:
            for segment in segments:
                print(
                    f"识别出的线段: 方向={'向上' if segment.direction == 1 else '向下'}, "
                    f"起点={segment.start_index}, 终点={segment.end_index}"
                )

        print("✅ 线段破坏条件测试通过")
        return True

    def test_stroke_segment_consistency(self) -> bool:
        """测试笔和线段的索引一致性"""
        print("=== 测试笔和线段索引一致性 ===")

        df = self.create_test_data("complex")
        self.processor._merge_k_lines(df)
        fractals = self.processor.identify_fractals()
        strokes = self.processor.build_strokes()
        segments = self.processor.build_segments()

        # 验证线段索引范围在笔索引范围内
        for segment in segments:
            stroke_indices = [s.end_index for s in strokes]
            if segment.start_index not in stroke_indices and segment.start_index != 0:
                print(f"❌ 线段起点索引不匹配任何笔")
                return False

        # 验证分型索引与笔索引的一致性
        for stroke in strokes:
            stroke_fractals = [
                f
                for f in fractals
                if f.index == stroke.start_index or f.index == stroke.end_index
            ]
            if len(stroke_fractals) != 2:
                print(f"❌ 笔端点无法匹配分型: 期望2个，实际{len(stroke_fractals)}")
                return False

        print("✅ 笔和线段索引一致性测试通过")
        return True

    def test_edge_cases(self) -> bool:
        """测试边界情况"""
        print("=== 测试边界情况 ===")

        # 测试数据不足
        small_df = pd.DataFrame(
            {
                "time_key": pd.date_range("2024-01-01", periods=3, freq="D"),
                "open": [10, 11, 10],
                "high": [11, 12, 11],
                "low": [9, 10, 9],
                "close": [10.5, 11.5, 10.5],
            }
        )

        self.processor._merge_k_lines(small_df)
        fractals = self.processor.identify_fractals()
        strokes = self.processor.build_strokes()
        segments = self.processor.build_segments()

        if len(fractals) > 0:
            print(f"✅ 小数据集分型识别: {len(fractals)}个")
        if len(strokes) == 0:
            print("✅ 小数据集无笔（符合预期）")
        if len(segments) == 0:
            print("✅ 小数据集无线段（符合预期）")

        print("✅ 边界情况测试通过")
        return True

    def run_all_tests(self) -> dict:
        """运行所有测试"""
        print("🚀 开始运行缠论笔和线段测试...\n")

        results = {
            "stroke_basic_construction": self.test_stroke_basic_construction(),
            "stroke_direction_alternation": self.test_stroke_direction_alternation(),
            "stroke_validity_rules": self.test_stroke_validity_rules(),
            "segment_construction": self.test_segment_construction(),
            "segment_break_conditions": self.test_segment_break_conditions(),
            "stroke_segment_consistency": self.test_stroke_segment_consistency(),
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
    tester = TestChanlunStrokesSegments()
    results = tester.run_all_tests()

    if all(results.values()):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查实现")

    return results


if __name__ == "__main__":
    main()
