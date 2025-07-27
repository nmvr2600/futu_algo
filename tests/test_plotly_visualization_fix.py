#!/usr/bin/env python3
"""
测试Plotly可视化修复
验证笔和线段的显示问题以及线段连续性问题
"""

import pandas as pd
import numpy as np
import sys
import os
import tempfile
from datetime import datetime, timedelta

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Stroke
from chanlun_plotly_visualizer import PlotlyChanlunVisualizer, generate_plotly_chart


class TestPlotlyVisualizationFix:
    """Plotly可视化修复测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()
        self.visualizer = PlotlyChanlunVisualizer()

    def create_test_data_for_continuity(self):
        """创建专门用于测试线段连续性的数据"""
        # 创建一个明显的趋势数据，确保能生成多个笔和线段
        data = []
        base_price = 100.0
        current_date = datetime(2024, 1, 1)
        
        # 创建5个明显的趋势段
        trends = [
            {'days': 8, 'direction': 1, 'step': 2.0},   # 上涨趋势
            {'days': 6, 'direction': -1, 'step': 1.5},  # 下跌趋势
            {'days': 7, 'direction': 1, 'step': 1.8},   # 上涨趋势
            {'days': 5, 'direction': -1, 'step': 2.2},  # 下跌趋势
            {'days': 6, 'direction': 1, 'step': 1.6},   # 上涨趋势
        ]
        
        day_count = 1
        for trend in trends:
            for i in range(trend['days']):
                price_change = trend['direction'] * trend['step']
                base_price += price_change
                
                # 添加一些随机波动
                open_price = base_price - 0.3 + np.random.normal(0, 0.2)
                high_price = base_price + 1.0 + np.random.normal(0, 0.3)
                low_price = base_price - 1.0 + np.random.normal(0, 0.3)
                close_price = base_price + np.random.normal(0, 0.2)
                
                data.append({
                    'time_key': current_date + timedelta(days=day_count),
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': 1000 + day_count * 50
                })
                day_count += 1
        
        return pd.DataFrame(data)

    def test_stroke_display(self):
        """测试笔是否正确显示"""
        print("=== 测试笔显示 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data_for_continuity()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 检查笔数据
            strokes = result.get('strokes', [])
            print(f"生成的笔数量: {len(strokes)}")
            
            # 验证笔数据是否完整
            valid_strokes = 0
            for i, stroke in enumerate(strokes):
                print(f"笔 {i+1}: 分形范围[{stroke.fractal_start},{stroke.fractal_end}], "
                      f"索引范围[{stroke.start_index},{stroke.end_index}], "
                      f"方向={'上涨' if stroke.direction == 1 else '下跌'}")
                
                # 检查笔数据完整性
                if (stroke.start_index is not None and stroke.end_index is not None and
                    stroke.start_price is not None and stroke.end_price is not None and
                    stroke.start_time_key is not None and stroke.end_time_key is not None):
                    valid_strokes += 1
            
            print(f"有效笔数量: {valid_strokes}")
            
            # 验证至少生成了一些笔
            assert len(strokes) >= 3, f"期望至少3个笔，实际生成{len(strokes)}个"
            assert valid_strokes >= 3, f"期望至少3个有效笔，实际生成{valid_strokes}个"
            
            # 验证笔的时间键是否存在
            strokes_with_time_keys = sum(1 for s in strokes if s.start_time_key is not None and s.end_time_key is not None)
            print(f"带有时间键的笔数量: {strokes_with_time_keys}")
            
            print("✅ 笔显示测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 笔显示测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_segment_continuity(self):
        """测试线段连续性"""
        print("=== 测试线段连续性 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data_for_continuity()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 检查线段数据
            segments = result.get('segments', [])
            strokes = result.get('strokes', [])
            print(f"生成的线段数量: {len(segments)}")
            print(f"生成的笔数量: {len(strokes)}")
            
            # 验证线段数据是否完整
            valid_segments = 0
            for i, segment in enumerate(segments):
                print(f"线段 {i+1}: 分形范围[{segment.fractal_start},{segment.fractal_end}], "
                      f"索引范围[{segment.start_index},{segment.end_index}], "
                      f"方向={'上涨' if segment.direction == 1 else '下跌'}")
                
                # 检查线段数据完整性
                if (segment.start_index is not None and segment.end_index is not None and
                    segment.start_price is not None and segment.end_price is not None and
                    segment.start_time_key is not None and segment.end_time_key is not None):
                    valid_segments += 1
            
            print(f"有效线段数量: {valid_segments}")
            
            # 验证至少生成了一些线段或笔
            # 如果线段数量太少，说明线段构建算法可能有问题
            if len(segments) == 1 and len(strokes) >= 3:
                print("⚠️  线段构建算法可能有问题：多个笔被合并为一个线段")
                print("❌ 线段连续性测试失败：线段构建不符合预期")
                return False
            
            # 如果有多个线段，验证线段连续性
            if len(segments) >= 2:
                # 验证线段连续性（除了首尾线段外，其余线段的起点应等于前一个线段的终点）
                continuity_issues = []
                if len(segments) >= 3:
                    for i in range(1, len(segments) - 1):  # 跳过首尾线段
                        prev_segment = segments[i-1]
                        curr_segment = segments[i]
                        
                        # 检查索引连续性
                        if curr_segment.start_index != prev_segment.end_index:
                            continuity_issues.append({
                                'type': '索引不连续',
                                'segment_index': i,
                                'prev_end_index': prev_segment.end_index,
                                'curr_start_index': curr_segment.start_index
                            })
                        
                        # 检查分形连续性
                        if curr_segment.fractal_start != prev_segment.fractal_end:
                            continuity_issues.append({
                                'type': '分形不连续',
                                'segment_index': i,
                                'prev_end_fractal': prev_segment.fractal_end,
                                'curr_start_fractal': curr_segment.fractal_start
                            })
                
                if continuity_issues:
                    print("发现连续性问题:")
                    for issue in continuity_issues:
                        print(f"  {issue}")
                    print("❌ 线段连续性测试失败")
                    return False
                else:
                    print("✅ 线段连续性测试通过")
                    return True
            elif len(segments) == 1:
                # 单个线段的情况下，验证其覆盖了所有笔
                segment = segments[0]
                first_stroke = strokes[0]
                last_stroke = strokes[-1]
                
                if (segment.start_index == first_stroke.start_index and 
                    segment.end_index == last_stroke.end_index):
                    print("✅ 单线段覆盖所有笔，测试通过")
                    return True
                else:
                    print("❌ 单线段未正确覆盖所有笔")
                    return False
            else:
                print("❌ 未生成有效的线段")
                return False
            
        except Exception as e:
            print(f"❌ 线段连续性测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_stroke_and_segment_visualization(self):
        """测试笔和线段的可视化显示"""
        print("=== 测试笔和线段可视化显示 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data_for_continuity()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 检查数据完整性
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            # 验证数据存在
            assert len(strokes) > 0, "没有生成笔数据"
            assert len(segments) > 0, "没有生成线段数据"
            
            # 使用临时目录测试图表生成
            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, "test_visualization.html")
                
                # 创建可视化图表
                fig = self.visualizer.create_comprehensive_chart(df, result, "TEST", chart_path)
                
                # 验证图表生成
                if os.path.exists(chart_path):
                    file_size = os.path.getsize(chart_path)
                    print(f"✅ 图表生成成功，文件大小: {file_size} bytes")
                    
                    # 验证文件内容不为空
                    if file_size > 1000:  # 至少应该有1KB
                        print("✅ 图表文件内容正常")
                        return True
                    else:
                        print("❌ 图表文件内容过小")
                        return False
                else:
                    print("❌ 图表文件未生成")
                    return False
                    
        except Exception as e:
            print(f"❌ 可视化显示测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_segment_endpoint_matching(self):
        """测试线段端点匹配（线段连接点应该重合）"""
        print("=== 测试线段端点匹配 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data_for_continuity()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取线段数据
            segments = result.get('segments', [])
            print(f"线段数量: {len(segments)}")
            
            if len(segments) < 2:
                print("⚠️  线段数量不足，无法测试端点匹配")
                return True
            
            # 检查相邻线段的端点是否匹配
            mismatched_segments = []
            for i in range(len(segments) - 1):
                current_segment = segments[i]
                next_segment = segments[i + 1]
                
                # 检查时间键是否匹配
                if current_segment.end_time_key != next_segment.start_time_key:
                    mismatched_segments.append({
                        'index': i,
                        'current_end_time': current_segment.end_time_key,
                        'next_start_time': next_segment.start_time_key
                    })
                
                # 检查价格是否匹配
                if abs(current_segment.end_price - next_segment.start_price) > 0.001:
                    mismatched_segments.append({
                        'index': i,
                        'current_end_price': current_segment.end_price,
                        'next_start_price': next_segment.start_price
                    })
            
            if mismatched_segments:
                print("发现端点不匹配的线段:")
                for mismatch in mismatched_segments:
                    print(f"  {mismatch}")
                print("❌ 线段端点匹配测试失败")
                return False
            else:
                print("✅ 线段端点匹配测试通过")
                return True
                
        except Exception as e:
            print(f"❌ 线段端点匹配测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行Plotly可视化修复测试...\n")
        
        tests = [
            ("笔显示测试", self.test_stroke_display),
            ("线段连续性测试", self.test_segment_continuity),
            ("可视化显示测试", self.test_stroke_and_segment_visualization),
            ("线段端点匹配测试", self.test_segment_endpoint_matching),
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
        print("📊 Plotly可视化修复测试总结报告")
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
    tester = TestPlotlyVisualizationFix()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有Plotly可视化修复测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())