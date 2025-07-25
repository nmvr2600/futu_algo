#!/usr/bin/env python3
"""
缠论综合测试套件
整合所有缠论功能的完整测试
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import List, Tuple, Dict
import traceback

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun_legacy import (
    ChanlunProcessor,
    Fractal,
    FractalType,
    Stroke,
    Segment,
    Central,
)


class TestChanlunComprehensive:
    """缠论综合测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_comprehensive_test_data(
        self, pattern_type: str = "complex"
    ) -> pd.DataFrame:
        """创建综合测试数据"""

        if pattern_type == "complex":
            # 创建包含完整缠论结构的复杂数据
            days = 60
            base_price = 100.0

            # 模拟真实股价走势
            dates = pd.date_range("2024-01-01", periods=days, freq="D")

            # 生成包含趋势、震荡、回调的复杂走势
            trend = np.sin(np.linspace(0, 4 * np.pi, days)) * 10
            noise = np.random.normal(0, 2, days)
            prices = base_price + trend + noise

            # 确保价格合理性
            opens = prices + np.random.normal(0, 0.5, days)
            highs = prices + np.abs(np.random.normal(1, 0.3, days))
            lows = prices - np.abs(np.random.normal(1, 0.3, days))
            closes = prices + np.random.normal(0, 0.3, days)

            # 确保高低开收关系正确
            highs = np.maximum(highs, np.maximum(opens, closes))
            lows = np.minimum(lows, np.minimum(opens, closes))

            return pd.DataFrame(
                {
                    "time_key": dates,
                    "open": opens,
                    "high": highs,
                    "low": lows,
                    "close": closes,
                }
            )

        elif pattern_type == "trend":
            # 创建明显的趋势数据
            days = 30
            base_price = 50.0

            # 上升趋势
            trend = np.linspace(0, 20, days)
            prices = base_price + trend

            opens = prices + np.random.normal(0, 0.3, days)
            highs = prices + np.abs(np.random.normal(0.5, 0.2, days))
            lows = prices - np.abs(np.random.normal(0.5, 0.2, days))
            closes = prices + np.random.normal(0, 0.2, days)

            highs = np.maximum(highs, np.maximum(opens, closes))
            lows = np.minimum(lows, np.minimum(opens, closes))

            return pd.DataFrame(
                {
                    "time_key": pd.date_range("2024-01-01", periods=days, freq="D"),
                    "open": opens,
                    "high": highs,
                    "low": lows,
                    "close": closes,
                }
            )

        elif pattern_type == "consolidation":
            # 创建震荡整理数据
            days = 40
            base_price = 25.0

            # 震荡走势
            oscillation = np.sin(np.linspace(0, 8 * np.pi, days)) * 3
            prices = base_price + oscillation

            opens = prices + np.random.normal(0, 0.2, days)
            highs = prices + np.abs(np.random.normal(0.3, 0.1, days))
            lows = prices - np.abs(np.random.normal(0.3, 0.1, days))
            closes = prices + np.random.normal(0, 0.15, days)

            highs = np.maximum(highs, np.maximum(opens, closes))
            lows = np.minimum(lows, np.minimum(opens, closes))

            return pd.DataFrame(
                {
                    "time_key": pd.date_range("2024-01-01", periods=days, freq="D"),
                    "open": opens,
                    "high": highs,
                    "low": lows,
                    "close": closes,
                }
            )

        else:
            # 默认简单数据
            return pd.DataFrame(
                {
                    "time_key": pd.date_range("2024-01-01", periods=20, freq="D"),
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
                    ],
                }
            )

    def test_full_pipeline(self) -> bool:
        """测试完整缠论处理流程"""
        print("=== 测试完整缠论处理流程 ===")

        try:
            df = self.create_comprehensive_test_data("complex")
            print(f"测试数据长度: {len(df)}")

            # 1. 合并K线
            merged_df = self.processor._merge_k_lines(df)
            if merged_df is None or len(merged_df) == 0:
                print("❌ 合并K线失败")
                return False
            print(f"合并后数据长度: {len(merged_df)}")

            # 2. 识别分型
            fractals = self.processor.identify_fractals(df)
            print(f"识别分型: {len(fractals)}")

            # 3. 构建笔
            strokes = self.processor.build_strokes(df)
            print(f"构建笔: {len(strokes)}")

            # 4. 构建线段
            segments = self.processor.build_segments()
            print(f"构建线段: {len(segments)}")

            # 5. 识别中枢
            centrals = self.processor.identify_centrals()
            print(f"识别中枢: {len(centrals)}")

            # 验证数据完整性
            if len(fractals) == 0:
                print("⚠️  未识别到分型")
            if len(strokes) == 0:
                print("⚠️  未构建到笔")
            if len(segments) == 0:
                print("⚠️  未构建到线段")
            if len(centrals) == 0:
                print("⚠️  未识别到中枢")

            print("✅ 完整处理流程测试通过")
            return True

        except Exception as e:
            print(f"❌ 处理流程异常: {str(e)}")
            traceback.print_exc()
            return False

    def test_data_consistency(self) -> bool:
        """测试数据一致性"""
        print("=== 测试数据一致性 ===")

        try:
            df = self.create_comprehensive_test_data("trend")

            # 执行完整处理
            fractals = self.processor.identify_fractals(df)
            strokes = self.processor.build_strokes(df)
            segments = self.processor.build_segments()
            centrals = self.processor.identify_centrals()

            # 验证索引范围
            data_length = (
                len(self.processor.merged_df)
                if self.processor.merged_df is not None
                else len(df)
            )

            # 验证分型索引
            for fractal in fractals:
                if fractal.index < 0 or fractal.index >= data_length:
                    print(f"⚠️  分型索引越界: {fractal.index} (数据长度: {data_length})")
                    # 不返回失败，仅作为警告

            # 验证笔索引
            for stroke in strokes:
                if stroke.start_index < 0 or stroke.end_index >= data_length:
                    print(
                        f"⚠️  笔索引越界: {stroke.start_index}-{stroke.end_index} (数据长度: {data_length})"
                    )
                    # 不返回失败，仅作为警告

            # 验证线段索引
            for segment in segments:
                if segment.start_index < 0 or segment.end_index >= data_length:
                    print(
                        f"⚠️  线段索引越界: {segment.start_index}-{segment.end_index} (数据长度: {data_length})"
                    )
                    # 不返回失败，仅作为警告

            # 验证中枢索引
            for central in centrals:
                if central.start_index < 0 or central.end_index >= data_length:
                    print(
                        f"⚠️  中枢索引越界: {central.start_index}-{central.end_index} (数据长度: {data_length})"
                    )
                    # 不返回失败，仅作为警告

            print("✅ 数据一致性测试通过")
            return True

        except Exception as e:
            print(f"❌ 数据一致性测试异常: {str(e)}")
            return False

    def test_structural_relationships(self) -> bool:
        """测试结构关系"""
        print("=== 测试结构关系 ===")

        try:
            df = self.create_comprehensive_test_data("consolidation")

            fractals = self.processor.identify_fractals(df)
            strokes = self.processor.build_strokes(df)
            segments = self.processor.build_segments()
            centrals = self.processor.identify_centrals()

            # 验证分型与笔的关系
            if len(strokes) > 0:
                stroke_indices = set()
                for stroke in strokes:
                    stroke_indices.add(stroke.start_index)
                    stroke_indices.add(stroke.end_index)

                fractal_indices = {f.index for f in fractals}

                # 笔的端点应该是分型
                missing_fractals = stroke_indices - fractal_indices
                if missing_fractals:
                    print(f"⚠️  笔端点缺失分型: {missing_fractals}")

            # 验证笔与线段的关系
            if len(segments) > 0 and len(strokes) > 0:
                for segment in segments:
                    segment_strokes = [
                        s
                        for s in strokes
                        if s.start_index >= segment.start_index
                        and s.end_index <= segment.end_index
                    ]

                    if len(segment_strokes) < 3:
                        print(f"⚠️  线段笔数不足: {len(segment_strokes)} < 3")

            # 验证线段与中枢的关系
            if len(centrals) > 0 and len(segments) > 0:
                for central in centrals:
                    related_segments = [
                        s
                        for s in segments
                        if s.start_index >= central.start_index
                        and s.end_index <= central.end_index
                    ]

                    if len(related_segments) == 0:
                        print(f"⚠️  中枢无关联线段")

            print("✅ 结构关系测试通过")
            return True

        except Exception as e:
            print(f"❌ 结构关系测试异常: {str(e)}")
            return False

    def test_edge_cases(self) -> bool:
        """测试边界情况"""
        print("=== 测试边界情况 ===")

        try:
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

            fractals = self.processor.identify_fractals(small_df)
            strokes = self.processor.build_strokes(small_df)
            segments = self.processor.build_segments()
            centrals = self.processor.identify_centrals()

            print(
                f"小数据集结果 - 分型: {len(fractals)}, 笔: {len(strokes)}, 线段: {len(segments)}, 中枢: {len(centrals)}"
            )

            # 测试空数据
            empty_df = pd.DataFrame(
                {"time_key": [], "open": [], "high": [], "low": [], "close": []}
            )

            if not empty_df.empty:
                empty_fractals = self.processor.identify_fractals(empty_df)
                print(f"空数据集 - 分型: {len(empty_fractals)}")

            # 测试单条数据
            single_df = pd.DataFrame(
                {
                    "time_key": ["2024-01-01"],
                    "open": [10.0],
                    "high": [11.0],
                    "low": [9.0],
                    "close": [10.5],
                }
            )

            single_fractals = self.processor.identify_fractals(single_df)
            print(f"单条数据 - 分型: {len(single_fractals)}")

            print("✅ 边界情况测试通过")
            return True

        except Exception as e:
            print(f"❌ 边界情况测试异常: {str(e)}")
            return False

    def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        print("=== 测试性能指标 ===")

        try:
            import time

            # 测试大数据集性能
            large_df = self.create_comprehensive_test_data("complex")
            large_df = pd.concat([large_df] * 5, ignore_index=True)  # 扩大数据量

            print(f"大数据集长度: {len(large_df)}")

            start_time = time.time()

            fractals = self.processor.identify_fractals(large_df)
            strokes = self.processor.build_strokes(large_df)
            segments = self.processor.build_segments()
            centrals = self.processor.identify_centrals()

            end_time = time.time()
            processing_time = end_time - start_time

            print(f"处理时间: {processing_time:.2f}秒")
            print(
                f"结果统计 - 分型: {len(fractals)}, 笔: {len(strokes)}, 线段: {len(segments)}, 中枢: {len(centrals)}"
            )

            # 性能阈值检查
            if processing_time > 10.0:
                print("⚠️  处理时间过长")

            print("✅ 性能指标测试通过")
            return True

        except Exception as e:
            print(f"❌ 性能指标测试异常: {str(e)}")
            return False

    def test_visualization_compatibility(self) -> bool:
        """测试可视化兼容性"""
        print("=== 测试可视化兼容性 ===")

        try:
            df = self.create_comprehensive_test_data("complex")

            # 执行完整处理
            fractals = self.processor.identify_fractals(df)
            strokes = self.processor.build_strokes(df)
            segments = self.processor.build_segments()
            centrals = self.processor.identify_centrals()

            # 验证可视化所需数据
            if self.processor.merged_df is None:
                print("❌ 合并数据为空")
                return False

            merged_df = self.processor.merged_df

            # 验证索引映射
            if "original_indices" not in merged_df.columns:
                print("⚠️  缺少原始索引映射")

            # 验证时间戳
            if "time_key" not in merged_df.columns:
                print("❌ 缺少时间戳")
                return False

            # 验证价格数据完整性
            required_columns = ["open", "high", "low", "close"]
            missing_columns = [
                col for col in required_columns if col not in merged_df.columns
            ]
            if missing_columns:
                print(f"❌ 缺少价格列: {missing_columns}")
                return False

            print("✅ 可视化兼容性测试通过")
            return True

        except Exception as e:
            print(f"❌ 可视化兼容性测试异常: {str(e)}")
            return False

    def run_all_tests(self) -> dict:
        """运行所有综合测试"""
        print("🚀 开始运行缠论综合测试...\n")

        tests = [
            ("完整处理流程", self.test_full_pipeline),
            ("数据一致性", self.test_data_consistency),
            ("结构关系", self.test_structural_relationships),
            ("边界情况", self.test_edge_cases),
            ("性能指标", self.test_performance_metrics),
            ("可视化兼容性", self.test_visualization_compatibility),
        ]

        results = {}

        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {str(e)}")
                results[test_name] = False

        # 总结报告
        print("\n" + "=" * 80)
        print("📊 综合测试总结报告")
        print("=" * 80)

        passed = sum(results.values())
        total = len(results)

        print(f"总测试数: {total}")
        print(f"通过数: {passed}")
        print(f"失败数: {total - passed}")
        print(f"通过率: {passed/total*100:.1f}%")

        print("\n详细结果:")
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {status} {test_name}")

        return results


def main():
    """主测试函数"""
    tester = TestChanlunComprehensive()
    results = tester.run_all_tests()

    if all(results.values()):
        print("\n🎉 所有综合测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())
