#!/usr/bin/env python3
"""
测试正确的笔和线段生成
验证能够生成多个不同的笔和线段
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


class TestProperStrokeSegmentGeneration:
    """正确笔和线段生成测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_multi_trend_data(self):
        """创建多趋势数据，确保能生成多个笔和线段"""
        data = []
        current_date = pd.Timestamp('2024-01-01')
        
        # 创建明显分型的数据，确保能生成多个笔
        # 每个趋势段需要足够的K线来形成分型
        
        # 趋势段1: 上涨趋势 - 需要形成底分型 -> 顶分型
        base_price = 100.0
        for i in range(10):
            price = base_price + i * 1.0
            # 创建波动以形成分型
            if i % 3 == 0:
                open_price = price - 0.3
                high_price = price + 0.5
                low_price = price - 0.5
                close_price = price + 0.2
            elif i % 3 == 1:
                open_price = price + 0.1
                high_price = price + 0.3
                low_price = price - 0.3
                close_price = price - 0.1
            else:
                open_price = price - 0.2
                high_price = price + 0.4
                low_price = price - 0.4
                close_price = price + 0.3
            
            data.append({
                'time_key': current_date + pd.Timedelta(days=len(data)),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000
            })
        
        base_price = data[-1]['close']
        
        # 趋势段2: 下跌趋势 - 需要形成顶分型 -> 底分型
        for i in range(10):
            price = base_price - i * 1.2
            # 创建波动以形成分型
            if i % 3 == 0:
                open_price = price + 0.3
                high_price = price + 0.5
                low_price = price - 0.5
                close_price = price - 0.2
            elif i % 3 == 1:
                open_price = price - 0.1
                high_price = price + 0.3
                low_price = price - 0.3
                close_price = price + 0.1
            else:
                open_price = price + 0.2
                high_price = price + 0.4
                low_price = price - 0.4
                close_price = price - 0.3
            
            data.append({
                'time_key': current_date + pd.Timedelta(days=len(data)),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000
            })
        
        base_price = data[-1]['close']
        
        # 趋势段3: 再次上涨 - 需要形成底分型 -> 顶分型
        for i in range(10):
            price = base_price + i * 1.5
            # 创建波动以形成分型
            if i % 3 == 0:
                open_price = price - 0.3
                high_price = price + 0.5
                low_price = price - 0.5
                close_price = price + 0.2
            elif i % 3 == 1:
                open_price = price + 0.1
                high_price = price + 0.3
                low_price = price - 0.3
                close_price = price - 0.1
            else:
                open_price = price - 0.2
                high_price = price + 0.4
                low_price = price - 0.4
                close_price = price + 0.3
            
            data.append({
                'time_key': current_date + pd.Timedelta(days=len(data)),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)

    def test_multi_trend_generation(self):
        """测试多趋势数据生成"""
        print("=== 测试多趋势数据生成 ===")
        
        try:
            # 创建多趋势数据
            df = self.create_multi_trend_data()
            print(f"多趋势数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            fractals = result.get('fractals', [])
            
            print(f"分型数量: {len(fractals)}")
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            # 显示分型信息
            if len(fractals) > 0:
                print("\n分型详情:")
                for i, fractal in enumerate(fractals[:10]):  # 显示前10个
                    type_str = "顶" if fractal.type.value == "top" else "底"
                    print(f"  分型 {fractal.idx}: {type_str}分型, 索引={fractal.index}, 价格={fractal.price:.2f}")
            
            # 显示笔信息
            if len(strokes) > 0:
                print("\n笔详情:")
                for i, stroke in enumerate(strokes[:10]):  # 显示前10个
                    direction_str = "上涨" if stroke.direction == 1 else "下跌"
                    print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                          f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}")
            
            # 显示线段信息
            if len(segments) > 0:
                print("\n线段详情:")
                for i, segment in enumerate(segments[:10]):  # 显示前10个
                    direction_str = "上涨" if segment.direction == 1 else "下跌"
                    print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
                          f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}")
            
            # 验证应该生成多个笔和线段
            if len(strokes) >= 3 and len(segments) >= 2:
                print("✅ 多趋势数据生成测试通过")
                return True
            else:
                print("❌ 多趋势数据生成测试失败：笔或线段数量不足")
                return False
                
        except Exception as e:
            print(f"❌ 多趋势数据生成测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def create_standard_chanlun_data(self):
        """创建标准缠论数据"""
        data = []
        current_date = pd.Timestamp('2024-01-01')
        
        # 创建标准的缠论走势数据
        prices = [
            # 第一波上涨
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
            # 回调
            109, 108, 107, 106, 105, 104, 103, 102, 101, 100,
            # 第二波上涨
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
            # 回调
            109, 108, 107, 106, 105, 104, 103, 102, 101, 100,
            # 第三波上涨
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
        ]
        
        # 添加波动以形成分型
        for i, base_price in enumerate(prices):
            # 根据位置添加波动
            if i % 5 == 0:
                open_price = base_price - 0.2
                high_price = base_price + 0.4
                low_price = base_price - 0.4
                close_price = base_price + 0.1
            elif i % 5 == 1:
                open_price = base_price + 0.1
                high_price = base_price + 0.3
                low_price = base_price - 0.3
                close_price = base_price - 0.2
            elif i % 5 == 2:
                open_price = base_price - 0.1
                high_price = base_price + 0.5
                low_price = base_price - 0.5
                close_price = base_price + 0.2
            elif i % 5 == 3:
                open_price = base_price + 0.2
                high_price = base_price + 0.2
                low_price = base_price - 0.2
                close_price = base_price - 0.1
            else:
                open_price = base_price - 0.3
                high_price = base_price + 0.3
                low_price = base_price - 0.3
                close_price = base_price + 0.3
            
            data.append({
                'time_key': current_date + pd.Timedelta(days=i),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000 + i * 10
            })
        
        return pd.DataFrame(data)

    def test_standard_chanlun_generation(self):
        """测试标准缠论数据生成"""
        print("=== 测试标准缠论数据生成 ===")
        
        try:
            # 创建标准缠论数据
            df = self.create_standard_chanlun_data()
            print(f"标准缠论数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            fractals = result.get('fractals', [])
            
            print(f"分型数量: {len(fractals)}")
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            # 验证应该生成足够的笔和线段
            if len(strokes) >= 4 and len(segments) >= 3:
                print("✅ 标准缠论数据生成测试通过")
                
                # 检查笔和线段是否不同
                if len(strokes) != len(segments):
                    print("✅ 笔和线段数量不同")
                else:
                    # 即使数量相同，检查具体内容
                    stroke_ranges = [(s.start_price, s.end_price) for s in strokes]
                    segment_ranges = [(s.start_price, s.end_price) for s in segments]
                    
                    if stroke_ranges != segment_ranges:
                        print("✅ 笔和线段内容不同")
                    else:
                        print("⚠️  笔和线段内容相同")
                
                return True
            else:
                print("❌ 标准缠论数据生成测试失败：笔或线段数量不足")
                print(f"  期望: 笔>=4, 线段>=3")
                print(f"  实际: 笔={len(strokes)}, 线段={len(segments)}")
                return False
                
        except Exception as e:
            print(f"❌ 标准缠论数据生成测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_visual_distinction(self):
        """测试视觉区分度"""
        print("=== 测试视觉区分度 ===")
        
        try:
            # 创建标准缠论数据
            df = self.create_standard_chanlun_data()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取笔和线段
            strokes = result.get('strokes', [])
            segments = result.get('segments', [])
            
            print(f"笔数量: {len(strokes)}")
            print(f"线段数量: {len(segments)}")
            
            # 验证应该有区别
            if len(strokes) > 0 and len(segments) > 0:
                # 检查是否完全相同
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
                    print("❌ 笔和线段完全相同！")
                    return False
                else:
                    print("✅ 笔和线段有区别")
                    return True
            else:
                print("❌ 数据不足无法验证")
                return False
                
        except Exception as e:
            print(f"❌ 视觉区分度测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行正确笔和线段生成测试...\n")
        
        tests = [
            ("多趋势数据生成测试", self.test_multi_trend_generation),
            ("标准缠论数据生成测试", self.test_standard_chanlun_generation),
            ("视觉区分度测试", self.test_visual_distinction),
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
        print("📊 正确笔和线段生成测试总结报告")
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
    tester = TestProperStrokeSegmentGeneration()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有正确笔和线段生成测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    exit(main())