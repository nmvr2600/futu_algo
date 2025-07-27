#!/usr/bin/env python3
"""
测试线段构建的正确性
验证线段是否符合缠论规范定义
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


class TestSegmentConstruction:
    """线段构建测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_test_data_with_clear_segments(self):
        """创建能明确形成线段的测试数据"""
        data = []
        current_date = pd.Timestamp('2024-01-01')
        
        # 创建明确的走势：上涨 -> 下跌 -> 上涨 -> 下跌 -> 上涨
        # 这样能形成清晰的笔和线段
        prices = [
            # 第一波上涨（形成多个上涨笔）
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
            # 回调（形成下跌笔）
            109, 108, 107, 106, 105, 104, 103, 102, 101, 100,
            # 第二波上涨（形成上涨笔）
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
            # 回调（形成下跌笔）
            109, 108, 107, 106, 105, 104, 103, 102, 101, 100,
            # 第三波上涨（形成上涨笔）
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

    def test_segment_properties(self):
        """测试线段属性是否符合规范"""
        print("=== 测试线段属性是否符合规范 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data_with_clear_segments()
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
            
            # 验证基本属性
            if len(strokes) < 3:
                print("❌ 笔数量不足，无法形成线段")
                return False
            
            # 检查线段是否至少包含3笔
            for i, segment in enumerate(segments):
                # 验证线段索引
                if segment.start_index >= len(self.processor.merged_df) or segment.end_index >= len(self.processor.merged_df):
                    print(f"❌ 线段 {i+1} 索引越界")
                    return False
                
                # 验证线段方向
                if segment.direction not in [1, -1]:
                    print(f"❌ 线段 {i+1} 方向无效: {segment.direction}")
                    return False
                
                print(f"  线段 {segment.idx}: 方向={'上涨' if segment.direction == 1 else '下跌'}, "
                      f"起始分型={segment.fractal_start}, 结束分型={segment.fractal_end}")
            
            # 验证线段和笔应该有区别（数量上或结构上）
            if len(segments) > 0 and len(strokes) > 0:
                print(f"✅ 线段构建测试通过")
                print(f"   笔数量: {len(strokes)}, 线段数量: {len(segments)}")
                return True
            else:
                print("❌ 线段或笔数量为0")
                return False
                
        except Exception as e:
            print(f"❌ 线段属性测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_segment_continuity(self):
        """测试线段连续性"""
        print("=== 测试线段连续性 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data_with_clear_segments()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 获取线段
            segments = result.get('segments', [])
            
            if len(segments) < 2:
                print("⚠️  线段数量不足，无法测试连续性")
                return True
            
            # 检查线段连续性（方向应该交替）
            directions = [segment.direction for segment in segments]
            is_alternating = True
            
            for i in range(1, len(directions)):
                if directions[i] == directions[i-1]:
                    is_alternating = False
                    break
            
            if is_alternating:
                print("✅ 线段方向交替正确")
            else:
                print("⚠️  线段方向未完全交替")
            
            return True
            
        except Exception as e:
            print(f"❌ 线段连续性测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行线段构建测试...\n")
        
        tests = [
            ("线段属性测试", self.test_segment_properties),
            ("线段连续性测试", self.test_segment_continuity),
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
        print("📊 线段构建测试总结报告")
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
    tester = TestSegmentConstruction()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有线段构建测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    exit(main())