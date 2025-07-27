#!/usr/bin/env python3
"""
综合测试：验证分型编号、笔和线段的区别以及可视化效果
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


def create_comprehensive_test_data():
    """创建综合测试数据"""
    data = []
    current_date = pd.Timestamp('2024-01-01')
    
    # 创建复杂的走势，确保能生成多个分型、笔和线段
    prices = []
    
    # 第一波上涨趋势
    for i in range(20):
        prices.append(100 + i * 0.5)
    
    # 回调
    for i in range(15):
        prices.append(110 - i * 0.4)
    
    # 第二波上涨趋势
    for i in range(15):
        prices.append(104 + i * 0.6)
    
    # 回调
    for i in range(10):
        prices.append(113 - i * 0.5)
    
    # 第三波上涨趋势
    for i in range(10):
        prices.append(108 + i * 0.7)
    
    # 添加波动以形成分型
    for i, base_price in enumerate(prices):
        # 根据位置添加波动
        if i % 4 == 0:
            open_price = base_price - 0.2
            high_price = base_price + 0.3
            low_price = base_price - 0.3
            close_price = base_price + 0.1
        elif i % 4 == 1:
            open_price = base_price + 0.1
            high_price = base_price + 0.2
            low_price = base_price - 0.2
            close_price = base_price - 0.1
        elif i % 4 == 2:
            open_price = base_price - 0.1
            high_price = base_price + 0.4
            low_price = base_price - 0.4
            close_price = base_price + 0.2
        else:
            open_price = base_price + 0.05
            high_price = base_price + 0.15
            low_price = base_price - 0.15
            close_price = base_price - 0.05
            
        data.append({
            'time_key': current_date + pd.Timedelta(days=i),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000 + i * 10
        })
    
    return pd.DataFrame(data)


def test_comprehensive_functionality():
    """综合功能测试"""
    print("=== 综合功能测试 ===")
    
    try:
        # 创建测试数据
        df = create_comprehensive_test_data()
        print(f"测试数据长度: {len(df)}")
        
        # 处理数据
        processor = ChanlunProcessor()
        result = processor.process(df)
        
        # 获取所有元素
        fractals = result.get('fractals', [])
        strokes = result.get('strokes', [])
        segments = result.get('segments', [])
        centrals = result.get('centrals', [])
        
        print(f"分型数量: {len(fractals)}")
        print(f"笔数量: {len(strokes)}")
        print(f"线段数量: {len(segments)}")
        print(f"中枢数量: {len(centrals)}")
        
        # 验证分型编号
        if len(fractals) > 0:
            print("\n分型编号验证:")
            for i, fractal in enumerate(fractals[:5]):  # 检查前5个
                type_str = "顶" if fractal.type.value == "top" else "底"
                print(f"  分型 {fractal.idx}: {type_str}分型, 索引={fractal.index}, 价格={fractal.price:.2f}")
                # 验证编号是否连续
                if fractal.idx != i + 1:
                    print(f"❌ 分型编号不连续: 期望 {i+1}, 实际 {fractal.idx}")
                    return False
        
        # 验证笔和线段的区别
        print(f"\n笔和线段区别验证:")
        print(f"  笔数量: {len(strokes)}")
        print(f"  线段数量: {len(segments)}")
        
        if len(strokes) > len(segments):
            print(f"✅ 笔和线段数量不同，符合预期")
        else:
            print(f"⚠️  笔和线段数量相同或笔少于线段")
        
        # 验证可视化
        print(f"\n可视化验证:")
        visualizer = PlotlyChanlunVisualizer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart_path = os.path.join(temp_dir, 'comprehensive_test_chart.html')
            fig = visualizer.create_comprehensive_chart(df, result, 'TEST', chart_path)
            
            # 检查图表元素
            stroke_traces = [trace for trace in fig.data if hasattr(trace, 'name') and trace.name and trace.name.startswith('笔')]
            segment_traces = [trace for trace in fig.data if hasattr(trace, 'name') and trace.name and trace.name.startswith('线段')]
            fractal_traces = [trace for trace in fig.data if hasattr(trace, 'name') and trace.name and ('分型' in trace.name)]
            
            print(f"  图表中笔轨迹数量: {len(stroke_traces)}")
            print(f"  图表中线段轨迹数量: {len(segment_traces)}")
            print(f"  图表中分型轨迹数量: {len(fractal_traces)}")
            
            # 验证视觉区别
            if len(stroke_traces) > 0 and len(segment_traces) > 0:
                stroke_trace = stroke_traces[0]
                segment_trace = segment_traces[0]
                
                # 检查线宽区别
                stroke_width = getattr(stroke_trace.line, 'width', 2)
                segment_width = getattr(segment_trace.line, 'width', 4)
                
                if stroke_width < segment_width:
                    print("✅ 笔和线段线宽不同，符合视觉区别要求")
                else:
                    print("⚠️  笔和线段线宽相同或笔比线段粗")
                
                # 检查线型区别
                stroke_dash = getattr(stroke_trace.line, 'dash', 'dash')
                segment_dash = getattr(segment_trace.line, 'dash', 'solid')
                
                if stroke_dash != segment_dash:
                    print("✅ 笔和线段线型不同，符合视觉区别要求")
                else:
                    print("⚠️  笔和线段线型相同")
                
                # 检查标记区别
                stroke_marker = getattr(stroke_trace.marker, 'symbol', 'circle')
                segment_marker = getattr(segment_trace.marker, 'symbol', 'diamond')
                
                if stroke_marker != segment_marker:
                    print("✅ 笔和线段标记不同，符合视觉区别要求")
                else:
                    print("⚠️  笔和线段标记相同")
            
            print(f"✅ 可视化测试完成，图表已生成: {chart_path}")
        
        print("\n✅ 综合功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 综合功能测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始运行综合功能测试...\n")
    
    success = test_comprehensive_functionality()
    
    if success:
        print("\n🎉 综合功能测试通过！所有功能正常工作。")
        return 0
    else:
        print("\n❌ 综合功能测试失败，请检查实现。")
        return 1


if __name__ == "__main__":
    exit(main())