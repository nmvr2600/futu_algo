#!/usr/bin/env python3
"""
测试分型编号功能
验证分型数据中包含idx字段以及编号显示功能
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Fractal, FractalType


class TestFractalNumbering:
    """分型编号测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()

    def create_test_data(self):
        """创建测试数据"""
        # 创建一个有明显分型的数据集
        data = []
        base_price = 100.0
        
        # 创建5个明显的分型模式
        patterns = [
            # 顶分型模式
            {'type': 'peak', 'steps': 3, 'direction': [1, -1, -1]},
            # 底分型模式
            {'type': 'valley', 'steps': 3, 'direction': [-1, 1, 1]},
            # 顶分型模式
            {'type': 'peak', 'steps': 3, 'direction': [1, -1, -1]},
            # 底分型模式
            {'type': 'valley', 'steps': 3, 'direction': [-1, 1, 1]},
            # 顶分型模式
            {'type': 'peak', 'steps': 3, 'direction': [1, -1, -1]},
        ]
        
        day_count = 1
        for pattern in patterns:
            for i, direction in enumerate(pattern['direction']):
                price_change = direction * 2.0
                base_price += price_change
                
                data.append({
                    'time_key': pd.Timestamp(f'2024-01-{day_count:02d}'),
                    'open': base_price - 0.5,
                    'high': base_price + 1.0,
                    'low': base_price - 1.0,
                    'close': base_price,
                    'volume': 1000 + day_count * 50
                })
                day_count += 1
        
        return pd.DataFrame(data)

    def test_fractal_data_structure(self):
        """测试分型数据结构包含idx字段"""
        print("=== 测试分型数据结构 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 检查分型数据
            fractals = result.get('fractals', [])
            print(f"生成的分型数量: {len(fractals)}")
            
            # 验证分型数据结构
            valid_fractals = 0
            for i, fractal in enumerate(fractals):
                print(f"分型 {i+1}: 类型={fractal.type.value}, 索引={fractal.index}, "
                      f"价格={fractal.price:.2f}, 编号={fractal.idx}")
                
                # 检查必需的字段是否存在
                required_fields = ['index', 'type', 'price', 'time_key', 'idx']
                has_all_fields = all(hasattr(fractal, field) for field in required_fields)
                
                if has_all_fields and fractal.idx > 0:
                    valid_fractals += 1
            
            print(f"有效分型数量: {valid_fractals}")
            
            # 验证至少生成了一些分型
            assert len(fractals) >= 2, f"期望至少2个分型，实际生成{len(fractals)}个"
            assert valid_fractals >= 2, f"期望至少2个有效分型，实际生成{valid_fractals}个"
            
            # 验证分型编号是否连续
            if len(fractals) > 1:
                expected_idx = 1
                for fractal in fractals:
                    assert fractal.idx == expected_idx, f"分型编号不连续: 期望{expected_idx}, 实际{fractal.idx}"
                    expected_idx += 1
                print("✅ 分型编号连续性验证通过")
            
            print("✅ 分型数据结构测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 分型数据结构测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_fractal_numbering_consistency(self):
        """测试分型编号一致性"""
        print("=== 测试分型编号一致性 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 检查分型数据
            fractals = result.get('fractals', [])
            
            if len(fractals) < 2:
                print("⚠️  分型数量不足，无法测试编号一致性")
                return True
            
            # 验证编号从1开始且连续
            for i, fractal in enumerate(fractals):
                expected_idx = i + 1
                assert fractal.idx == expected_idx, f"分型{i+1}编号错误: 期望{expected_idx}, 实际{fractal.idx}"
            
            print("✅ 分型编号一致性测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 分型编号一致性测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_fractal_type_distribution(self):
        """测试分型类型分布"""
        print("=== 测试分型类型分布 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 检查分型数据
            fractals = result.get('fractals', [])
            
            # 统计顶分型和底分型数量
            top_fractals = [f for f in fractals if f.type == FractalType.TOP]
            bottom_fractals = [f for f in fractals if f.type == FractalType.BOTTOM]
            
            print(f"顶分型数量: {len(top_fractals)}")
            print(f"底分型数量: {len(bottom_fractals)}")
            print(f"总分型数量: {len(fractals)}")
            
            # 验证分型编号在不同类型间是否连续
            all_fractals = sorted(fractals, key=lambda x: x.index)
            for i, fractal in enumerate(all_fractals):
                expected_idx = i + 1
                assert fractal.idx == expected_idx, f"分型编号错误: 期望{expected_idx}, 实际{fractal.idx}"
            
            print("✅ 分型类型分布测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 分型类型分布测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有分型编号测试"""
        print("🚀 开始运行分型编号测试...\n")
        
        tests = [
            ("分型数据结构测试", self.test_fractal_data_structure),
            ("分型编号一致性测试", self.test_fractal_numbering_consistency),
            ("分型类型分布测试", self.test_fractal_type_distribution),
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
        print("📊 分型编号测试总结报告")
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
    tester = TestFractalNumbering()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有分型编号测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())