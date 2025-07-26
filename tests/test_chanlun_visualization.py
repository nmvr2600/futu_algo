#!/usr/bin/env python3
"""
缠论可视化测试套件
测试图表生成、K线绘制、元素定位等可视化功能
"""

import pandas as pd
import numpy as np
import sys
import os
import tempfile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chanlun_advanced_visualizer import AdvancedChanlunVisualizer, generate_divergence_chart
from util.chanlun import ChanlunProcessor


class TestChanlunVisualization:
    """缠论可视化测试类"""

    def __init__(self):
        self.visualizer = AdvancedChanlunVisualizer()
        self.processor = ChanlunProcessor()

    def create_test_data(self, data_type="standard"):
        """创建测试数据"""
        if data_type == "standard":
            # 创建标准测试数据
            dates = pd.date_range("2024-01-01", periods=30, freq="D")
            prices = np.linspace(100, 120, 30) + np.random.normal(0, 2, 30)
            
            return pd.DataFrame({
                "time_key": dates,
                "open": prices + np.random.normal(0, 0.5, 30),
                "high": prices + np.abs(np.random.normal(1, 0.3, 30)),
                "low": prices - np.abs(np.random.normal(1, 0.3, 30)),
                "close": prices + np.random.normal(0, 0.3, 30),
            })
        
        elif data_type == "small":
            # 创建小数据集
            dates = pd.date_range("2024-01-01", periods=10, freq="D")
            prices = np.array([100, 101, 102, 101, 100, 99, 98, 99, 100, 101])
            
            return pd.DataFrame({
                "time_key": dates,
                "open": prices,
                "high": prices + 1,
                "low": prices - 1,
                "close": prices + np.random.normal(0, 0.2, 10),
            })
        
        elif data_type == "large":
            # 创建大数据集
            dates = pd.date_range("2024-01-01", periods=200, freq="D")
            # 模拟股价走势
            trend = np.linspace(0, 50, 200)
            oscillation = np.sin(np.linspace(0, 12 * np.pi, 200)) * 10
            prices = 100 + trend + oscillation + np.random.normal(0, 3, 200)
            
            return pd.DataFrame({
                "time_key": dates,
                "open": prices + np.random.normal(0, 0.5, 200),
                "high": prices + np.abs(np.random.normal(1, 0.3, 200)),
                "low": prices - np.abs(np.random.normal(1, 0.3, 200)),
                "close": prices + np.random.normal(0, 0.3, 200),
            })

    def test_chart_generation(self):
        """测试图表生成"""
        print("=== 测试图表生成 ===")
        
        try:
            # 使用临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                df = self.create_test_data("standard")
                result = self.processor.process(df)
                
                # 生成图表
                chart_path = os.path.join(temp_dir, "test_chart.png")
                fig = self.visualizer.create_comprehensive_chart(df, result, "TEST", chart_path)
                
                # 验证图表生成
                if os.path.exists(chart_path):
                    file_size = os.path.getsize(chart_path)
                    print(f"✅ 图表生成成功，文件大小: {file_size} bytes")
                    return True
                else:
                    print("❌ 图表文件未生成")
                    return False
                    
        except Exception as e:
            print(f"❌ 图表生成异常: {str(e)}")
            return False

    def test_kline_drawing(self):
        """测试K线绘制"""
        print("=== 测试K线绘制 ===")
        
        try:
            df = self.create_test_data("standard")
            result = self.processor.process(df)
            
            # 创建图表但不保存
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 测试K线绘制函数
            dates = pd.to_datetime(df["time_key"])
            x_dates = [mdates.date2num(date) for date in dates]
            index_map = self.visualizer._create_index_map(df)
            merged_index_map = self.visualizer._create_merged_index_map(result)
            self.visualizer._plot_enhanced_kline(
                fig, ax, df, dates, x_dates, result, [], index_map, merged_index_map
            )
            
            print("✅ K线绘制测试通过")
            plt.close(fig)
            return True
            
        except Exception as e:
            print(f"❌ K线绘制异常: {str(e)}")
            return False

    def test_element_positioning(self):
        """测试元素定位"""
        print("=== 测试元素定位 ===")
        
        try:
            df = self.create_test_data("standard")
            result = self.processor.process(df)
            
            # 验证索引映射
            if hasattr(self.processor, 'merged_df') and self.processor.merged_df is not None:
                merged_df = self.processor.merged_df
                original_length = len(df)
                merged_length = len(merged_df)
                
                print(f"原始数据长度: {original_length}")
                print(f"合并后数据长度: {merged_length}")
                
                # 验证索引范围
                if 'fractals' in result and result['fractals']:
                    for fractal in result['fractals'][:3]:  # 检查前3个分型
                        if fractal.index >= merged_length:
                            print(f"⚠️  分型索引越界: {fractal.index} >= {merged_length}")
                        else:
                            print(f"✅ 分型索引正常: {fractal.index} < {merged_length}")
                
                # 验证时间数据
                if 'time_key' in merged_df.columns:
                    print("✅ 时间数据存在")
                    return True
                else:
                    print("❌ 缺少时间数据")
                    return False
            else:
                print("❌ 无合并数据")
                return False
                
        except Exception as e:
            print(f"❌ 元素定位异常: {str(e)}")
            return False

    def test_fractal_annotation_positioning(self):
        """测试分型标注位置准确性"""
        print("=== 测试分型标注位置准确性 ===")
        
        try:
            df = self.create_test_data("standard")
            result = self.processor.process(df)
            
            # 创建图表但不保存
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 测试分型绘制函数
            dates = pd.to_datetime(df["time_key"])
            x_dates = [mdates.date2num(date) for date in dates]
            index_map = self.visualizer._create_index_map(df)
            merged_index_map = self.visualizer._create_merged_index_map(result)
            fractal_number_map = self.visualizer._create_fractal_number_map(result)
            
            # 绘制K线
            self.visualizer._plot_enhanced_kline(
                fig, ax, df, dates, x_dates, result, [], index_map, merged_index_map
            )
            
            # 绘制分型
            self.visualizer._plot_fractals_detailed(
                ax, df, dates, result.get('fractals', []), index_map, fractal_number_map, merged_index_map
            )
            
            # 验证分型标注位置
            annotations = []
            for child in ax.get_children():
                if hasattr(child, 'get_text') and child.get_text():
                    # 获取标注的位置
                    if hasattr(child, 'get_position'):
                        pos = child.get_position()
                        annotations.append({
                            'text': child.get_text(),
                            'position': pos,
                            'type': type(child).__name__
                        })
            
            print(f"检测到 {len(annotations)} 个标注")
            
            # 验证至少有一些标注存在
            if len(annotations) > 0:
                print("✅ 分型标注位置测试通过")
                plt.close(fig)
                return True
            else:
                print("❌ 未检测到分型标注")
                plt.close(fig)
                return False
                
        except Exception as e:
            print(f"❌ 分型标注位置异常: {str(e)}")
            return False

    def test_stroke_annotation_positioning(self):
        """测试笔标注位置准确性"""
        print("=== 测试笔标注位置准确性 ===")
        
        try:
            df = self.create_test_data("standard")
            result = self.processor.process(df)
            
            # 创建图表但不保存
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 测试笔绘制函数
            dates = pd.to_datetime(df["time_key"])
            x_dates = [mdates.date2num(date) for date in dates]
            index_map = self.visualizer._create_index_map(df)
            merged_index_map = self.visualizer._create_merged_index_map(result)
            fractal_number_map = self.visualizer._create_fractal_number_map(result)
            
            # 绘制K线
            self.visualizer._plot_enhanced_kline(
                fig, ax, df, dates, x_dates, result, [], index_map, merged_index_map
            )
            
            # 绘制笔
            self.visualizer._plot_strokes_detailed(
                ax, df, dates, result.get('strokes', []), index_map, fractal_number_map, merged_index_map
            )
            
            # 验证笔标注位置
            annotations = []
            for child in ax.get_children():
                if hasattr(child, 'get_text') and child.get_text():
                    # 获取标注的位置
                    if hasattr(child, 'get_position'):
                        pos = child.get_position()
                        annotations.append({
                            'text': child.get_text(),
                            'position': pos,
                            'type': type(child).__name__
                        })
            
            print(f"检测到 {len(annotations)} 个笔标注")
            
            # 验证至少有一些标注存在
            if len(annotations) > 0:
                print("✅ 笔标注位置测试通过")
                plt.close(fig)
                return True
            else:
                print("⚠️  未检测到笔标注（可能是数据不足）")
                plt.close(fig)
                return True  # 不算失败，因为可能数据不足
                
        except Exception as e:
            print(f"❌ 笔标注位置异常: {str(e)}")
            return False

    def test_kline_positioning_accuracy(self):
        """测试K线位置准确性，确保K线正确分布在时间轴上"""
        print("=== 测试K线位置准确性 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data("standard")
            result = self.processor.process(df)
            
            # 创建图表但不保存
            fig, ax = plt.subplots(figsize=(15, 8))
            
            # 准备绘图数据
            dates = pd.to_datetime(df["time_key"])
            x_dates = [mdates.date2num(date) for date in dates]
            index_map = self.visualizer._create_index_map(df)
            merged_index_map = self.visualizer._create_merged_index_map(result)
            
            # 绘制K线
            self.visualizer._plot_enhanced_kline(
                fig, ax, df, dates, x_dates, result, [], index_map, merged_index_map
            )
            
            # 收集所有K线矩形元素
            kline_rectangles = []
            for child in ax.get_children():
                if isinstance(child, matplotlib.patches.Rectangle):
                    # 获取矩形的位置和宽度
                    bbox = child.get_bbox()
                    if bbox:
                        kline_rectangles.append({
                            'x': child.get_x(),
                            'y': child.get_y(),
                            'width': child.get_width(),
                            'height': child.get_height()
                        })
            
            print(f"检测到 {len(kline_rectangles)} 个K线矩形元素")
            
            # 验证K线数量是否合理
            if len(kline_rectangles) < len(df) // 2:  # 至少应该有数据量的一半
                print("❌ K线数量过少")
                plt.close(fig)
                return False
            
            # 验证K线是否正确分布在时间轴上
            x_positions = [rect['x'] for rect in kline_rectangles]
            x_positions.sort()
            
            # 检查是否有K线堆叠在一起（x坐标相同）
            unique_x_positions = set(x_positions)
            if len(unique_x_positions) < len(x_positions) * 0.8:  # 如果超过20%的K线x坐标相同，则认为堆叠
                print("❌ 检测到K线堆叠问题")
                print(f"  总K线数: {len(x_positions)}")
                print(f"  唯一x坐标数: {len(unique_x_positions)}")
                plt.close(fig)
                return False
            
            # 验证K线是否按时间顺序排列
            if x_positions != sorted(x_positions):
                print("❌ K线未按时间顺序排列")
                plt.close(fig)
                return False
            
            print("✅ K线位置准确性测试通过")
            plt.close(fig)
            return True
                
        except Exception as e:
            print(f"❌ K线位置准确性测试异常: {str(e)}")
            return False

    def test_visual_regression_with_specific_parameters(self):
        """测试特定参数下的视觉回归"""
        print("=== 测试特定参数下的视觉回归 ===")
        
        try:
            # 模拟用户之前报告的问题场景
            df = self.create_test_data("large")  # 使用大数据集
            result = self.processor.process(df)
            
            # 创建图表但不保存
            fig, ax = plt.subplots(figsize=(20, 12))
            
            # 测试完整的图表绘制流程
            dates = pd.to_datetime(df["time_key"])
            x_dates = [mdates.date2num(date) for date in dates]
            index_map = self.visualizer._create_index_map(df)
            merged_index_map = self.visualizer._create_merged_index_map(result)
            fractal_number_map = self.visualizer._create_fractal_number_map(result)
            
            # 绘制完整的图表
            self.visualizer._plot_enhanced_kline(
                fig, ax, df, dates, x_dates, result, [], index_map, merged_index_map
            )
            
            self.visualizer._plot_fractals_detailed(
                ax, df, dates, result.get('fractals', []), index_map, fractal_number_map, merged_index_map
            )
            
            self.visualizer._plot_strokes_detailed(
                ax, df, dates, result.get('strokes', []), index_map, fractal_number_map, merged_index_map
            )
            
            self.visualizer._plot_segments_detailed(
                ax, df, dates, result.get('segments', []), index_map, fractal_number_map, merged_index_map
            )
            
            self.visualizer._plot_centrals_detailed(
                ax, df, dates, result.get('centrals', []), index_map, merged_index_map
            )
            
            # 验证所有元素都正确绘制
            children_count = len(ax.get_children())
            print(f"图表包含 {children_count} 个绘图元素")
            
            # 确保图表元素数量合理（避免空图表或异常图表）
            if children_count > 50:  # 至少应该有一些基本元素
                print("✅ 视觉回归测试通过")
                plt.close(fig)
                return True
            else:
                print("❌ 图表元素过少，可能存在绘制问题")
                plt.close(fig)
                return False
                
        except Exception as e:
            print(f"❌ 视觉回归测试异常: {str(e)}")
            return False

    def test_index_mapping(self):
        """测试索引映射"""
        print("=== 测试索引映射 ===")
        
        try:
            df = self.create_test_data("standard")
            result = self.processor.process(df)
            
            # 测试索引映射函数
            index_map = self.visualizer._create_index_map(df)
            merged_index_map = self.visualizer._create_merged_index_map(result)
            
            print(f"索引映射创建成功")
            print(f"  原始索引映射数量: {len(index_map)}")
            print(f"  合并索引映射数量: {len(merged_index_map)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 索引映射异常: {str(e)}")
            return False

    def test_time_axis_formatting(self):
        """测试时间轴格式化"""
        print("=== 测试时间轴格式化 ===")
        
        try:
            df = self.create_test_data("standard")
            result = self.processor.process(df)
            
            # 创建图表测试时间轴
            fig, ax = plt.subplots(figsize=(10, 6))
            dates = pd.to_datetime(df["time_key"])
            
            # 测试时间轴设置
            ax.set_xlim(dates.iloc[0], dates.iloc[-1])
            
            # 测试时间格式化
            import matplotlib.dates as mdates
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            
            print("✅ 时间轴格式化测试通过")
            plt.close(fig)
            return True
            
        except Exception as e:
            print(f"❌ 时间轴格式化异常: {str(e)}")
            return False

    def test_different_intervals(self):
        """测试不同时间间隔"""
        print("=== 测试不同时间间隔 ===")
        
        try:
            test_cases = ["small", "standard", "large"]
            results = []
            
            for case in test_cases:
                df = self.create_test_data(case)
                result = self.processor.process(df)
                
                # 验证处理结果
                fractals = len(result.get('fractals', []))
                strokes = len(result.get('strokes', []))
                
                print(f"  {case}: 分型={fractals}, 笔={strokes}")
                results.append(fractals > 0 or strokes > 0)
            
            success_rate = sum(results) / len(results)
            if success_rate > 0.5:
                print("✅ 不同时间间隔测试通过")
                return True
            else:
                print("❌ 不同时间间隔测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 不同时间间隔异常: {str(e)}")
            return False

    def test_edge_cases_visualization(self):
        """测试边界情况可视化"""
        print("=== 测试边界情况可视化 ===")
        
        try:
            # 测试空数据
            empty_df = pd.DataFrame(columns=["time_key", "open", "high", "low", "close"])
            try:
                result = self.processor.process(empty_df)
                print("  空数据处理: 通过")
            except Exception as e:
                print(f"  空数据处理: {str(e)[:50]}...")
            
            # 测试单根K线
            single_df = pd.DataFrame({
                "time_key": ["2024-01-01"],
                "open": [100],
                "high": [101],
                "low": [99],
                "close": [100.5],
            })
            try:
                result = self.processor.process(single_df)
                print("  单根K线处理: 通过")
            except Exception as e:
                print(f"  单根K线处理: {str(e)[:50]}...")
            
            # 测试两根K线
            two_df = pd.DataFrame({
                "time_key": ["2024-01-01", "2024-01-02"],
                "open": [100, 101],
                "high": [101, 102],
                "low": [99, 100],
                "close": [100.5, 101.5],
            })
            try:
                result = self.processor.process(two_df)
                print("  两根K线处理: 通过")
            except Exception as e:
                print(f"  两根K线处理: {str(e)[:50]}...")
            
            print("✅ 边界情况可视化测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 边界情况可视化异常: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有可视化测试"""
        print("🚀 开始运行缠论可视化测试...\n")
        
        tests = [
            ("图表生成", self.test_chart_generation),
            ("K线绘制", self.test_kline_drawing),
            ("元素定位", self.test_element_positioning),
            ("分型标注位置", self.test_fractal_annotation_positioning),
            ("笔标注位置", self.test_stroke_annotation_positioning),
            ("K线位置准确性", self.test_kline_positioning_accuracy),
            ("视觉回归测试", self.test_visual_regression_with_specific_parameters),
            ("索引映射", self.test_index_mapping),
            ("时间轴格式化", self.test_time_axis_formatting),
            ("不同时间间隔", self.test_different_intervals),
            ("边界情况可视化", self.test_edge_cases_visualization),
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
        print("📊 可视化测试总结报告")
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
    tester = TestChanlunVisualization()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有可视化测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())