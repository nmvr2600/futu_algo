#!/usr/bin/env python3
"""
测试笔和线段的区别
验证笔和线段构建逻辑是否正确
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


class TestStrokeSegmentDifference:
    """笔和线段区别测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_test_data(self):
        """创建测试数据 - 明确的多笔模式，应该能形成多个线段"""
        data = []
        
        # 创建明显趋势的数据，确保能生成多个方向的笔
        base_price = 100.0
        current_date = pd.Timestamp('2024-01-01')
        
        # 模式1: 明显的上涨趋势 (形成多个底分型和顶分型)
        prices1 = [100, 95, 105, 100, 110, 105, 115, 110, 120]  # 上涨趋势
        
        # 模式2: 明显的下跌趋势
        prices2 = [120, 125, 115, 120, 110, 115, 105, 110, 100]  # 下跌趋势
        
        # 模式3: 震荡模式
        prices3 = [100, 105, 95, 100, 90, 95, 85, 90, 80]  # 下跌趋势
        
        all_prices = prices1 + prices2 + prices3
        
        for i, price in enumerate(all_prices):
            data.append({
                'time_key': current_date + pd.Timedelta(days=i),
                'open': price - 0.5,
                'high': price + 1.0,
                'low': price - 1.0,
                'close': price,
                'volume': 1000 + i * 50
            })
        
        return pd.DataFrame(data)

    def test_stroke_segment_difference(self):
        """测试笔和线段的区别"""
        print("=== 测试笔和线段的区别 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            self.processor.process(df)
            
            # 获取笔和线段
            strokes = self.processor.strokes
            segments = self.processor.segments
            
            print(f"生成的笔数量: {len(strokes)}")
            print(f"生成的线段数量: {len(segments)}")
            
            # 显示笔的详细信息
            if len(strokes) > 0:
                print("\n笔详情:")
                for i, stroke in enumerate(strokes):
                    direction_str = "上涨" if stroke.direction == 1 else "下跌"
                    print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                          f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
                          f"索引 {stroke.start_index}->{stroke.end_index}")
            
            # 显示线段的详细信息
            if len(segments) > 0:
                print("\n线段详情:")
                for i, segment in enumerate(segments):
                    direction_str = "上涨" if segment.direction == 1 else "下跌"
                    print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
                          f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
                          f"索引 {segment.start_index}->{segment.end_index}")
            
            # 验证笔和线段应该不同
            if len(strokes) > 0 and len(segments) > 0:
                # 检查数量是否不同
                if len(strokes) != len(segments):
                    print("✅ 笔和线段数量不同，符合预期")
                else:
                    print("⚠️  笔和线段数量相同，可能存在问题")
                
                # 检查具体内容是否不同
                stroke_info = [(s.start_index, s.end_index, s.direction) for s in strokes]
                segment_info = [(s.start_index, s.end_index, s.direction) for s in segments]
                
                if stroke_info != segment_info:
                    print("✅ 笔和线段的具体内容不同，符合预期")
                else:
                    print("❌ 笔和线段的具体内容相同，线段构建逻辑可能有问题")
                    return False
                
                # 验证线段应该包含多个笔
                if len(segments) < len(strokes):
                    print("✅ 线段数量少于笔数量，符合线段聚合笔的逻辑")
                else:
                    print("⚠️  线段数量不少于笔数量，需要进一步检查")
            
            # 特别检查：如果笔和线段完全一样，说明有问题
            if len(strokes) == len(segments):
                identical = True
                for s, seg in zip(strokes, segments):
                    if (s.start_index != seg.start_index or 
                        s.end_index != seg.end_index or 
                        s.start_price != seg.start_price or 
                        s.end_price != seg.end_price or
                        s.direction != seg.direction):
                        identical = False
                        break
                
                if identical:
                    print("❌ 严重问题：笔和线段完全相同！")
                    return False
                else:
                    print("✅ 笔和线段不完全相同")
            
            print("✅ 笔和线段区别测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 笔和线段区别测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_specific_pattern(self):
        """测试特定模式 - 确保能生成不同的笔和线段"""
        print("=== 测试特定模式 ===")
        
        try:
            # 创建一个明确的模式：上涨->下跌->上涨
            data = []
            base_price = 100.0
            current_date = pd.Timestamp('2024-01-01')
            
            # 明确的三段趋势
            # 第一段：上涨趋势 - 应该形成上涨笔
            prices1 = [100, 102, 104, 106, 108]
            # 第二段：下跌趋势 - 应该形成下跌笔  
            prices2 = [108, 106, 104, 102, 100]
            # 第三段：上涨趋势 - 应该形成上涨笔
            prices3 = [100, 102, 104, 106, 108]
            
            all_prices = prices1 + prices2 + prices3
            
            for i, price in enumerate(all_prices):
                data.append({
                    'time_key': current_date + pd.Timedelta(days=i),
                    'open': price,
                    'high': price + 0.5,
                    'low': price - 0.5,
                    'close': price,
                    'volume': 1000
                })
            
            df = pd.DataFrame(data)
            print(f"特定模式测试数据长度: {len(df)}")
            
            # 处理数据
            self.processor.process(df)
            
            # 获取笔和线段
            strokes = self.processor.strokes
            segments = self.processor.segments
            
            print(f"特定模式生成的笔数量: {len(strokes)}")
            print(f"特定模式生成的线段数量: {len(segments)}")
            
            # 应该至少有2个笔（一个上涨，一个下跌，然后可能又一个上涨）
            # 应该有2个线段（上涨线段，下跌线段）
            
            if len(strokes) >= 2 and len(segments) >= 2:
                print("✅ 特定模式测试通过")
                return True
            else:
                print("❌ 特定模式测试失败：笔或线段数量不足")
                return False
                
        except Exception as e:
            print(f"❌ 特定模式测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行笔和线段区别测试...\n")
        
        tests = [
            ("笔和线段区别测试", self.test_stroke_segment_difference),
            ("特定模式测试", self.test_specific_pattern),
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
        print("\n⚠️  部分测试失败，笔和线段可能存在问题")
        return 1


if __name__ == "__main__":
    exit(main())