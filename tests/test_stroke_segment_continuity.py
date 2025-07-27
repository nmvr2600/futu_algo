#!/usr/bin/env python3
"""
专门测试笔和线段连续性的测试用例
验证笔和线段在构建过程中是否保持连续性
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


class TestStrokeSegmentContinuity:
    """笔和线段连续性测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_data_for_continuity_test(self):
        """创建能明确生成多个笔和线段的测试数据"""
        data = []
        current_date = pd.Timestamp('2024-01-01')
        
        # 创建复杂的走势，确保能生成多个笔和线段
        # 模式：上涨 -> 回调 -> 上涨 -> 回调 -> 上涨 -> 回调 -> 上涨
        prices = []
        
        # 第一波上涨（10根K线）
        for i in range(10):
            prices.append(100 + i * 1.5)
        
        # 第一次回调（6根K线）
        for i in range(6):
            prices.append(115 - i * 1.2)
        
        # 第二波上涨（8根K线）
        for i in range(8):
            prices.append(107.8 + i * 1.8)
        
        # 第二次回调（5根K线）
        for i in range(5):
            prices.append(122.2 - i * 1.6)
        
        # 第三波上涨（7根K线）
        for i in range(7):
            prices.append(114.2 + i * 1.4)
        
        # 第三次回调（6根K线）
        for i in range(6):
            prices.append(124 - i * 1.3)
        
        # 第四波上涨（8根K线）
        for i in range(8):
            prices.append(116.2 + i * 1.7)
        
        # 添加波动以形成分型
        for i, base_price in enumerate(prices):
            # 根据位置添加波动
            if i % 3 == 0:
                open_price = base_price - 0.3
                high_price = base_price + 0.5
                low_price = base_price - 0.5
                close_price = base_price + 0.2
            elif i % 3 == 1:
                open_price = base_price + 0.1
                high_price = base_price + 0.3
                low_price = base_price - 0.3
                close_price = base_price - 0.1
            else:
                open_price = base_price - 0.2
                high_price = base_price + 0.4
                low_price = base_price - 0.4
                close_price = base_price + 0.1
                
            data.append({
                'time_key': current_date + pd.Timedelta(days=i),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000 + i * 10
            })
        
        return pd.DataFrame(data)

    def test_stroke_continuity(self):
        """测试笔的连续性"""
        print("=== 测试笔的连续性 ===")
        
        try:
            # 创建测试数据
            df = self.create_data_for_continuity_test()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔数据
            strokes = result.get('strokes', [])
            print(f"生成的笔数量: {len(strokes)}")
            
            if len(strokes) < 2:
                print("⚠️  笔数量不足，无法测试连续性")
                return True
            
            # 验证笔的连续性
            continuity_issues = []
            for i in range(1, len(strokes)):
                prev_stroke = strokes[i-1]
                curr_stroke = strokes[i]
                
                # 笔应该首尾相连
                if prev_stroke.end_index != curr_stroke.start_index:
                    continuity_issues.append({
                        'index': i,
                        'prev_end_index': prev_stroke.end_index,
                        'curr_start_index': curr_stroke.start_index,
                        'gap': curr_stroke.start_index - prev_stroke.end_index
                    })
                
                # 笔的方向应该交替
                if prev_stroke.direction == curr_stroke.direction:
                    continuity_issues.append({
                        'index': i,
                        'issue': 'direction_not_alternating',
                        'prev_direction': prev_stroke.direction,
                        'curr_direction': curr_stroke.direction
                    })
            
            # 显示前几个笔的详细信息
            print("前5个笔的详细信息:")
            for i, stroke in enumerate(strokes[:5]):
                direction_str = "上涨" if stroke.direction == 1 else "下跌"
                print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                      f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
                      f"索引 {stroke.start_index}->{stroke.end_index}")
            
            if continuity_issues:
                print("发现连续性问题:")
                for issue in continuity_issues:
                    print(f"  {issue}")
                print("❌ 笔连续性测试失败")
                return False
            else:
                print("✅ 笔连续性测试通过")
                return True
                
        except Exception as e:
            print(f"❌ 笔连续性测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_segment_continuity(self):
        """测试线段的连续性"""
        print("=== 测试线段的连续性 ===")
        
        try:
            # 创建测试数据
            df = self.create_data_for_continuity_test()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取线段数据
            segments = result.get('segments', [])
            strokes = result.get('strokes', [])
            print(f"生成的线段数量: {len(segments)}")
            print(f"生成的笔数量: {len(strokes)}")
            
            if len(segments) < 1:
                print("⚠️  线段数量不足，无法测试连续性")
                return True
            
            if len(segments) == 1:
                print("✅ 单个线段测试通过")
                return True
            
            # 验证线段的连续性
            continuity_issues = []
            for i in range(1, len(segments)):
                prev_segment = segments[i-1]
                curr_segment = segments[i]
                
                # 线段应该首尾相连（允许小的间隙）
                index_gap = curr_segment.start_index - prev_segment.end_index
                fractal_gap = curr_segment.fractal_start - prev_segment.fractal_end
                
                if index_gap > 2:  # 允许最多2个K线的间隙
                    continuity_issues.append({
                        'index': i,
                        'type': 'index_gap_too_large',
                        'prev_end_index': prev_segment.end_index,
                        'curr_start_index': curr_segment.start_index,
                        'gap': index_gap
                    })
                
                if fractal_gap > 1:  # 允许最多1个分型的间隙
                    continuity_issues.append({
                        'index': i,
                        'type': 'fractal_gap_too_large',
                        'prev_end_fractal': prev_segment.fractal_end,
                        'curr_start_fractal': curr_segment.fractal_start,
                        'gap': fractal_gap
                    })
            
            # 显示线段的详细信息
            print("所有线段的详细信息:")
            for i, segment in enumerate(segments):
                direction_str = "上涨" if segment.direction == 1 else "下跌"
                print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
                      f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
                      f"索引 {segment.start_index}->{segment.end_index}")
            
            if continuity_issues:
                print("发现连续性问题:")
                for issue in continuity_issues:
                    print(f"  {issue}")
                print("❌ 线段连续性测试失败")
                return False
            else:
                print("✅ 线段连续性测试通过")
                return True
                
        except Exception as e:
            print(f"❌ 线段连续性测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_stroke_direction_alternation(self):
        """测试笔方向交替性"""
        print("=== 测试笔方向交替性 ===")
        
        try:
            # 创建测试数据
            df = self.create_data_for_continuity_test()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔数据
            strokes = result.get('strokes', [])
            print(f"笔数量: {len(strokes)}")
            
            if len(strokes) < 2:
                print("⚠️  笔数量不足，无法测试方向交替性")
                return True
            
            # 验证相邻笔方向必须相反
            direction_issues = []
            for i in range(1, len(strokes)):
                prev_stroke = strokes[i-1]
                curr_stroke = strokes[i]
                
                if prev_stroke.direction == curr_stroke.direction:
                    direction_issues.append({
                        'index': i,
                        'prev_direction': prev_stroke.direction,
                        'curr_direction': curr_stroke.direction
                    })
            
            if direction_issues:
                print("发现方向交替问题:")
                for issue in direction_issues:
                    direction_str = lambda d: "上涨" if d == 1 else "下跌"
                    print(f"  笔{i-1}({direction_str(issue['prev_direction'])}) 和 笔{i}({direction_str(issue['curr_direction'])}) 方向相同")
                print("❌ 笔方向交替性测试失败")
                return False
            else:
                print("✅ 笔方向交替性测试通过")
                return True
                
        except Exception as e:
            print(f"❌ 笔方向交替性测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_segment_coverage(self):
        """测试线段是否正确覆盖笔"""
        print("=== 测试线段是否正确覆盖笔 ===")
        
        try:
            # 创建测试数据
            df = self.create_data_for_continuity_test()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取数据
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            if len(strokes) < 3:
                print("⚠️  笔数量不足，无法测试线段覆盖")
                return True
            
            if len(segments) < 1:
                print("⚠️  线段数量不足，无法测试线段覆盖")
                return True
            
            # 验证线段是否正确覆盖笔
            coverage_issues = []
            
            # 检查所有笔是否都被线段覆盖
            covered_stroke_indices = set()
            for segment in segments:
                # 找到被这个线段覆盖的所有笔
                for stroke in strokes:
                    if (stroke.start_index >= segment.start_index and 
                        stroke.end_index <= segment.end_index):
                        covered_stroke_indices.add(stroke.idx)
            
            # 检查是否有未被覆盖的笔
            all_stroke_indices = set(s.idx for s in strokes)
            uncovered_stroke_indices = all_stroke_indices - covered_stroke_indices
            
            if uncovered_stroke_indices:
                coverage_issues.append({
                    'type': 'uncovered_strokes',
                    'indices': list(uncovered_stroke_indices)
                })
            
            if coverage_issues:
                print("发现覆盖问题:")
                for issue in coverage_issues:
                    print(f"  {issue}")
                print("❌ 线段覆盖测试失败")
                return False
            else:
                print("✅ 线段覆盖测试通过")
                return True
                
        except Exception as e:
            print(f"❌ 线段覆盖测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行笔和线段连续性测试...\n")
        
        tests = [
            ("笔连续性测试", self.test_stroke_continuity),
            ("线段连续性测试", self.test_segment_continuity),
            ("笔方向交替性测试", self.test_stroke_direction_alternation),
            ("线段覆盖测试", self.test_segment_coverage),
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
        print("📊 笔和线段连续性测试总结报告")
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
    tester = TestStrokeSegmentContinuity()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有笔和线段连续性测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())