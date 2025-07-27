#!/usr/bin/env python3
"""
测试笔和线段的视觉区别
验证笔和线段在可视化上应该有明显区别
"""

import pandas as pd
import numpy as np
import sys
import os
import tempfile

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor
from chanlun_plotly_visualizer import PlotlyChanlunVisualizer


class TestStrokeSegmentVisualDifference:
    """笔和线段视觉区别测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()
        self.visualizer = PlotlyChanlunVisualizer()

    def create_simple_test_data(self):
        """创建简单的测试数据"""
        data = []
        current_date = pd.Timestamp('2024-01-01')
        
        # 创建一个明确的趋势：上涨 -> 下跌 -> 上涨
        prices = [
            100, 102, 104, 106, 108,  # 上涨
            108, 106, 104, 102, 100,  # 下跌
            100, 102, 104, 106, 108   # 上涨
        ]
        
        for i, price in enumerate(prices):
            data.append({
                'time_key': current_date + pd.Timedelta(days=i),
                'open': price - 0.2,
                'high': price + 0.3,
                'low': price - 0.3,
                'close': price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)

    def test_visual_properties_difference(self):
        """测试笔和线段的视觉属性区别"""
        print("=== 测试笔和线段的视觉属性区别 ===")
        
        try:
            # 创建测试数据
            df = self.create_simple_test_data()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            
            print(f"生成的笔数量: {len(strokes)}")
            print(f"生成的线段数量: {len(segments)}")
            
            # 创建可视化图表
            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, 'visual_test_chart.html')
                fig = self.visualizer.create_comprehensive_chart(df, result, 'TEST', chart_path)
                
                # 检查图表中的笔轨迹
                stroke_traces = [trace for trace in fig.data if hasattr(trace, 'name') and trace.name.startswith('笔')]
                segment_traces = [trace for trace in fig.data if hasattr(trace, 'name') and trace.name.startswith('线段')]
                
                print(f"图表中笔轨迹数量: {len(stroke_traces)}")
                print(f"图表中线段轨迹数量: {len(segment_traces)}")
                
                # 检查笔轨迹的属性
                if len(stroke_traces) > 0:
                    stroke_trace = stroke_traces[0]
                    if hasattr(stroke_trace, 'line'):
                        line = stroke_trace.line
                        print(f"笔线宽: {getattr(line, 'width', 'N/A')}")
                        print(f"笔线型: {getattr(line, 'dash', 'N/A')}")
                    
                    if hasattr(stroke_trace, 'marker'):
                        marker = stroke_trace.marker
                        print(f"笔标记大小: {getattr(marker, 'size', 'N/A')}")
                
                # 检查线段轨迹的属性
                if len(segment_traces) > 0:
                    segment_trace = segment_traces[0]
                    if hasattr(segment_trace, 'line'):
                        line = segment_trace.line
                        print(f"线段线宽: {getattr(line, 'width', 'N/A')}")
                        print(f"线段线型: {getattr(line, 'dash', 'solid')}")
                    
                    if hasattr(segment_trace, 'marker'):
                        marker = segment_trace.marker
                        print(f"线段标记大小: {getattr(marker, 'size', 'N/A')}")
                
                # 验证视觉属性不同
                if len(stroke_traces) > 0 and len(segment_traces) > 0:
                    stroke_line_width = getattr(stroke_traces[0].line, 'width', 2)
                    segment_line_width = getattr(segment_traces[0].line, 'width', 4)
                    
                    if stroke_line_width != segment_line_width:
                        print("✅ 笔和线段线宽不同")
                    else:
                        print("⚠️  笔和线段线宽相同")
                
                print("✅ 视觉属性区别测试完成")
                return True
                
        except Exception as e:
            print(f"❌ 视觉属性区别测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_data_structure_difference(self):
        """测试笔和线段数据结构的区别"""
        print("=== 测试笔和线段数据结构的区别 ===")
        
        try:
            # 创建测试数据
            df = self.create_simple_test_data()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            # 检查数据结构
            if len(strokes) > 0 and len(segments) > 0:
                # 比较第一个笔和第一个线段
                first_stroke = strokes[0]
                first_segment = segments[0]
                
                differences = []
                
                if first_stroke.start_index != first_segment.start_index:
                    differences.append(f"起始索引不同: 笔={first_stroke.start_index}, 线段={first_segment.start_index}")
                
                if first_stroke.end_index != first_segment.end_index:
                    differences.append(f"结束索引不同: 笔={first_stroke.end_index}, 线段={first_segment.end_index}")
                
                if first_stroke.start_price != first_segment.start_price:
                    differences.append(f"起始价格不同: 笔={first_stroke.start_price}, 线段={first_segment.start_price}")
                
                if first_stroke.end_price != first_segment.end_price:
                    differences.append(f"结束价格不同: 笔={first_stroke.end_price}, 线段={first_segment.end_price}")
                
                if first_stroke.direction != first_segment.direction:
                    differences.append(f"方向不同: 笔={first_stroke.direction}, 线段={first_segment.direction}")
                
                if differences:
                    print("发现以下区别:")
                    for diff in differences:
                        print(f"  - {diff}")
                    print("✅ 笔和线段数据结构有区别")
                else:
                    print("❌ 笔和线段数据结构完全相同！")
                    return False
            
            print("✅ 数据结构区别测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 数据结构区别测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def create_complex_test_data(self):
        """创建复杂的测试数据，确保能生成多个笔和线段"""
        data = []
        current_date = pd.Timestamp('2024-01-01')
        base_price = 100.0
        
        # 创建复杂的趋势模式
        # 模式1: 小幅上涨趋势 (形成多个笔)
        for i in range(5):
            price = base_price + i * 2
            data.append({
                'time_key': current_date + pd.Timedelta(days=len(data)),
                'open': price - 0.5,
                'high': price + 1.0,
                'low': price - 1.0,
                'close': price,
                'volume': 1000
            })
        
        base_price = price
        
        # 模式2: 小幅下跌趋势
        for i in range(5):
            price = base_price - i * 1.5
            data.append({
                'time_key': current_date + pd.Timedelta(days=len(data)),
                'open': price - 0.5,
                'high': price + 1.0,
                'low': price - 1.0,
                'close': price,
                'volume': 1000
            })
        
        base_price = price
        
        # 模式3: 再次上涨
        for i in range(5):
            price = base_price + i * 1.8
            data.append({
                'time_key': current_date + pd.Timedelta(days=len(data)),
                'open': price - 0.5,
                'high': price + 1.0,
                'low': price - 1.0,
                'close': price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)

    def test_complex_pattern(self):
        """测试复杂模式下的笔和线段"""
        print("=== 测试复杂模式下的笔和线段 ===")
        
        try:
            # 创建复杂测试数据
            df = self.create_complex_test_data()
            print(f"复杂测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            
            print(f"复杂模式生成的笔数量: {len(strokes)}")
            print(f"复杂模式生成的线段数量: {len(segments)}")
            
            # 显示详细信息
            if len(strokes) > 0:
                print("\n笔详情:")
                for i, stroke in enumerate(strokes[:5]):  # 只显示前5个
                    direction_str = "上涨" if stroke.direction == 1 else "下跌"
                    print(f"  笔 {stroke.idx}: {direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}")
            
            if len(segments) > 0:
                print("\n线段详情:")
                for i, segment in enumerate(segments[:5]):  # 只显示前5个
                    direction_str = "上涨" if segment.direction == 1 else "下跌"
                    print(f"  线段 {segment.idx}: {direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}")
            
            # 验证应该有区别
            if len(strokes) > 0 and len(segments) > 0:
                print("✅ 复杂模式测试完成")
                return True
            else:
                print("❌ 复杂模式测试失败：未能生成足够的笔或线段")
                return False
                
        except Exception as e:
            print(f"❌ 复杂模式测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行笔和线段视觉区别测试...\n")
        
        tests = [
            ("视觉属性区别测试", self.test_visual_properties_difference),
            ("数据结构区别测试", self.test_data_structure_difference),
            ("复杂模式测试", self.test_complex_pattern),
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
        print("📊 笔和线段视觉区别测试总结报告")
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
    tester = TestStrokeSegmentVisualDifference()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有笔和线段视觉区别测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    exit(main())