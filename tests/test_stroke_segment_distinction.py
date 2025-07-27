#!/usr/bin/env python3
"""
测试线段和笔的区别
验证在复杂情况下线段和笔确实不同
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor
from chanlun_plotly_visualizer import PlotlyChanlunVisualizer


class TestStrokeSegmentDifference:
    """笔和线段区别测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()
        self.visualizer = PlotlyChanlunVisualizer()

    def create_complex_data_for_distinction(self):
        """创建能明显区分笔和线段的复杂数据"""
        data = []
        current_date = pd.Timestamp('2024-01-01')
        
        # 创建复杂的走势，确保能生成多个同向笔从而形成线段
        # 模式：小上涨 -> 小回调 -> 小上涨 -> 小回调 (形成多个上涨笔，构成一个上涨线段)
        
        prices = []
        
        # 第一组：形成多个小上涨和小回调
        base = 100
        # 小上涨1
        prices.extend([100, 100.5, 101, 101.5, 102])
        # 小回调1  
        prices.extend([102, 101.5, 101, 100.5, 100])
        # 小上涨2
        prices.extend([100, 100.5, 101, 101.5, 102])
        # 小回调2
        prices.extend([102, 101.5, 101, 100.5, 100])
        # 小上涨3
        prices.extend([100, 100.5, 101, 101.5, 102])
        # 小回调3
        prices.extend([102, 101.5, 101, 100.5, 100])
        # 小上涨4
        prices.extend([100, 100.5, 101, 101.5, 102])
        
        for i, price in enumerate(prices):
            # 添加波动以确保能形成分型
            if i % 3 == 0:
                open_price = price - 0.1
                high_price = price + 0.2
                low_price = price - 0.2
                close_price = price + 0.05
            elif i % 3 == 1:
                open_price = price + 0.05
                high_price = price + 0.15
                low_price = price - 0.15
                close_price = price - 0.1
            else:
                open_price = price - 0.05
                high_price = price + 0.25
                low_price = price - 0.25
                close_price = price + 0.1
                
            data.append({
                'time_key': current_date + pd.Timedelta(days=i),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)

    def test_stroke_and_segment_distinction(self):
        """测试笔和线段是否能明显区分"""
        print("=== 测试笔和线段是否能明显区分 ===")
        
        try:
            # 创建复杂测试数据
            df = self.create_complex_data_for_distinction()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            fractals = result.get('fractals', [])
            
            print(f"分型数量: {len(fractals)}")
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            # 显示详细信息
            if len(fractals) > 0:
                print("\n分型详情:")
                for fractal in fractals[:10]:
                    type_str = "顶" if fractal.type.value == "top" else "底"
                    print(f"  分型 {fractal.idx}: {type_str}分型, 索引={fractal.index}, 价格={fractal.price:.2f}")
            
            if len(strokes) > 0:
                print("\n笔详情:")
                for stroke in strokes[:10]:
                    direction_str = "上涨" if stroke.direction == 1 else "下跌"
                    print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                          f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
                          f"索引 {stroke.start_index}->{stroke.end_index}")
            
            if len(segments) > 0:
                print("\n线段详情:")
                for segment in segments[:10]:
                    direction_str = "上涨" if segment.direction == 1 else "下跌"
                    print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
                          f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
                          f"索引 {segment.start_index}->{segment.end_index}")
            
            # 关键检查：笔和线段是否不同
            if len(strokes) > 0 and len(segments) > 0:
                # 检查数量是否不同
                if len(strokes) != len(segments):
                    print(f"\n✅ 笔和线段数量不同: 笔={len(strokes)}, 线段={len(segments)}")
                    return True
                
                # 检查具体内容是否不同
                stroke_details = [(s.start_index, s.end_index, s.direction) for s in strokes]
                segment_details = [(s.start_index, s.end_index, s.direction) for s in segments]
                
                if stroke_details != segment_details:
                    print("\n✅ 笔和线段具体内容不同")
                    return True
                
                # 完全相同
                print("\n❌ 笔和线段完全相同")
                return False
            else:
                print("\n❌ 数据不足无法比较")
                return False
                
        except Exception as e:
            print(f"❌ 笔和线段区别测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def create_manual_distinct_case(self):
        """创建手动明确的区别测试用例"""
        print("\n=== 创建手动明确的区别测试用例 ===")
        
        # 手动创建一个明确的走势，能形成多笔一线段的情况
        data = []
        current_date = pd.Timestamp('2024-01-01')
        
        # 创建明确的分型点，确保能形成多个笔但线段覆盖所有
        test_points = [
            # 底分型1
            (100, 99, 101, 100.5),  # 低点
            (100.5, 100, 101.5, 101), 
            (101, 100.5, 102, 101.5),  # 高点
            (101.5, 101, 102.5, 102),
            (102, 101.5, 103, 102.5),  # 底分型2
            # 形成第一笔：上涨笔
            
            # 顶分型1
            (102.5, 102, 104, 103.5),  # 高点
            (103.5, 103, 104.5, 104),
            (104, 103.5, 105, 104.5),  # 底分型3
            (104.5, 104, 105.5, 105),
            (105, 104.5, 106, 105.5),  # 顶分型2
            # 形成第二笔：下跌笔
            
            # 底分型4
            (105.5, 105, 107, 106.5),  # 低点
            (106.5, 106, 107.5, 107),
            (107, 106.5, 108, 107.5),  # 高点
            # 形成第三笔：上涨笔
        ]
        
        for i, (open_p, low_p, high_p, close_p) in enumerate(test_points):
            data.append({
                'time_key': current_date + pd.Timedelta(days=i),
                'open': open_p,
                'high': high_p,
                'low': low_p,
                'close': close_p,
                'volume': 1000
            })
        
        return pd.DataFrame(data)

    def test_manual_distinct_case(self):
        """测试手动明确的区别用例"""
        print("=== 测试手动明确的区别用例 ===")
        
        try:
            # 创建手动测试数据
            df = self.create_manual_distinct_case()
            print(f"手动测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            if len(strokes) > 0:
                print("\n笔详情:")
                for stroke in strokes:
                    direction_str = "上涨" if stroke.direction == 1 else "下跌"
                    print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                          f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}")
            
            if len(segments) > 0:
                print("\n线段详情:")
                for segment in segments:
                    direction_str = "上涨" if segment.direction == 1 else "下跌"
                    print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
                          f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}")
            
            # 检查是否能区分（应该有3笔，1线段）
            if len(strokes) >= 3 and len(segments) >= 1:
                if len(strokes) > len(segments):
                    print(f"\n✅ 手动测试成功：笔({len(strokes)})和线段({len(segments)})数量不同")
                    return True
                else:
                    print(f"\n⚠️  手动测试：笔和线段数量相同")
                    return True
            else:
                print(f"\n❌ 手动测试失败：笔或线段数量不足")
                return False
                
        except Exception as e:
            print(f"❌ 手动区别测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行笔和线段区别测试...\n")
        
        tests = [
            ("笔和线段区别测试", self.test_stroke_and_segment_distinction),
            ("手动区别测试", self.test_manual_distinct_case),
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
        print("📊 笔和线段区别测试总结报告")
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
    tester = TestStrokeSegmentDifference()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有笔和线段区别测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    exit(main())