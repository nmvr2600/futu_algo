#!/usr/bin/env python3
"""
分型编号功能最终验证测试
验证分型编号显示功能的完整实现
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


class TestFractalNumberingFinal:
    """分型编号功能最终验证测试类"""

    def __init__(self):
        self.processor = ChanlunProcessor()
        self.visualizer = PlotlyChanlunVisualizer()

    def create_test_data(self):
        """创建测试数据"""
        # 创建一个有明显分型的数据集
        data = []
        base_price = 100.0
        
        # 创建多个分型模式
        patterns = [
            # 底分型
            {'type': 'valley', 'steps': [100, 95, 100]},
            # 顶分型
            {'type': 'peak', 'steps': [100, 105, 100]},
            # 底分型
            {'type': 'valley', 'steps': [100, 97, 100]},
            # 顶分型
            {'type': 'peak', 'steps': [100, 108, 100]},
            # 底分型
            {'type': 'valley', 'steps': [100, 92, 100]},
            # 顶分型
            {'type': 'peak', 'steps': [100, 110, 100]},
        ]
        
        day_count = 1
        for pattern in patterns:
            for price in pattern['steps']:
                data.append({
                    'time_key': pd.Timestamp(f'2024-01-{day_count:02d}'),
                    'open': price - 0.5,
                    'high': price + 1.0,
                    'low': price - 1.0,
                    'close': price,
                    'volume': 1000 + day_count * 50
                })
                day_count += 1
        
        return pd.DataFrame(data)

    def test_complete_fractal_numbering_implementation(self):
        """测试完整的分型编号实现"""
        print("=== 测试完整的分型编号实现 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data()
            print(f"测试数据长度: {len(df)}")
            
            # 处理数据
            result = self.processor.process(df)
            
            # 检查分型数据
            fractals = result.get('fractals', [])
            print(f"生成的分型数量: {len(fractals)}")
            
            # 验证分型编号
            if len(fractals) > 0:
                print("分型详情:")
                for i, fractal in enumerate(fractals):
                    type_str = "顶" if fractal.type.value == "top" else "底"
                    print(f"  分型 {fractal.idx}: {type_str}分型, 价格={fractal.price:.2f}")
                
                # 验证编号连续性
                expected_idx = 1
                for fractal in fractals:
                    assert fractal.idx == expected_idx, f"分型编号不连续: 期望{expected_idx}, 实际{fractal.idx}"
                    expected_idx += 1
                print("✅ 分型编号连续性验证通过")
            
            # 创建可视化图表
            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, 'final_test_chart.html')
                fig = self.visualizer.create_comprehensive_chart(df, result, 'TEST', chart_path)
                
                # 验证图表生成
                assert os.path.exists(chart_path), "图表文件未生成"
                file_size = os.path.getsize(chart_path)
                assert file_size > 1000, f"图表文件过小: {file_size} bytes"
                print(f"✅ 图表生成成功，文件大小: {file_size} bytes")
                
                # 验证图表包含分型轨迹
                fractal_traces = [trace for trace in fig.data if hasattr(trace, 'name') and '分型' in trace.name]
                assert len(fractal_traces) > 0, "图表中未找到分型轨迹"
                print(f"✅ 图表包含 {len(fractal_traces)} 个分型相关轨迹")
                
                # 验证图表包含文本元素
                text_traces = [trace for trace in fig.data if hasattr(trace, 'mode') and 'text' in getattr(trace, 'mode', '')]
                assert len(text_traces) > 0, "图表中未找到文本元素"
                print(f"✅ 图表包含 {len(text_traces)} 个文本轨迹")
            
            print("✅ 完整分型编号实现测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 完整分型编号实现测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_fractal_numbering_visual_appearance(self):
        """测试分型编号的视觉效果"""
        print("=== 测试分型编号的视觉效果 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 创建可视化图表
            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, 'visual_test_chart.html')
                fig = self.visualizer.create_comprehensive_chart(df, result, 'TEST', chart_path)
                
                # 检查分型轨迹的样式
                fractal_traces = [trace for trace in fig.data if '分型' in trace.name]
                
                for trace in fractal_traces:
                    # 检查是否包含文本
                    assert hasattr(trace, 'text'), "分型轨迹缺少文本属性"
                    assert trace.text is not None, "分型轨迹文本为空"
                    
                    # 检查文本位置
                    assert hasattr(trace, 'textposition'), "分型轨迹缺少文本位置属性"
                    
                    # 检查文本字体
                    if hasattr(trace, 'textfont') and trace.textfont is not None:
                        print("✅ 分型轨迹包含文本字体设置")
                
                # 检查顶分型和底分型
                top_fractal_traces = [trace for trace in fig.data if trace.name == "顶分型"]
                bottom_fractal_traces = [trace for trace in fig.data if trace.name == "底分型"]
                
                print(f"顶分型轨迹数量: {len(top_fractal_traces)}")
                print(f"底分型轨迹数量: {len(bottom_fractal_traces)}")
                
                assert len(top_fractal_traces) > 0 or len(bottom_fractal_traces) > 0, "未找到分型轨迹"
                
                print("✅ 分型编号视觉效果测试通过")
                return True
                
        except Exception as e:
            print(f"❌ 分型编号视觉效果测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_fractal_numbering_hover_information(self):
        """测试分型编号的悬停信息"""
        print("=== 测试分型编号的悬停信息 ===")
        
        try:
            # 创建测试数据
            df = self.create_test_data()
            
            # 处理数据
            result = self.processor.process(df)
            
            # 创建可视化图表
            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, 'hover_test_chart.html')
                fig = self.visualizer.create_comprehensive_chart(df, result, 'TEST', chart_path)
                
                # 检查悬停模板
                fractal_traces = [trace for trace in fig.data if '分型' in trace.name]
                
                for trace in fractal_traces:
                    if hasattr(trace, 'hovertemplate') and trace.hovertemplate is not None:
                        hover_template = trace.hovertemplate
                        print(f"悬停模板: {hover_template}")
                        # 检查是否包含编号信息
                        assert '分型 #' in hover_template, "悬停模板缺少分型编号信息"
                        print("✅ 悬停模板包含分型编号信息")
                
                print("✅ 分型编号悬停信息测试通过")
                return True
                
        except Exception as e:
            print(f"❌ 分型编号悬停信息测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有最终验证测试"""
        print("🚀 开始运行分型编号功能最终验证测试...\n")
        
        tests = [
            ("完整分型编号实现测试", self.test_complete_fractal_numbering_implementation),
            ("分型编号视觉效果测试", self.test_fractal_numbering_visual_appearance),
            ("分型编号悬停信息测试", self.test_fractal_numbering_hover_information),
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
        print("📊 分型编号功能最终验证测试总结报告")
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
    tester = TestFractalNumberingFinal()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 所有分型编号功能最终验证测试通过！")
        print("✅ 分型编号显示功能已成功实现！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())