#!/usr/bin/env python3
"""
测试线段绘制功能的脚本
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom.chanlun_selector_demo import get_stock_data
from util.chanlun import ChanlunProcessor
from chanlun_advanced_visualizer import AdvancedChanlunVisualizer


def test_segments_functionality():
    """测试线段功能是否正确工作"""
    
    print("=== 测试线段绘制功能 ===")
    
    try:
        # 获取测试数据
        stock_code = "0700.HK"
        data = get_stock_data(stock_code, period="2y", interval="1d")
        
        if len(data) < 30:
            print("数据不足，需要至少30根K线")
            return
        
        print(f"获取了 {len(data)} 根K线数据")
        
        # 缠论分析
        processor = ChanlunProcessor()
        result = processor.process(data)
        
        # 检查结果
        print(f"提取到笔: {len(processor.strokes)}")
        print(f"提取到线段: {len(processor.segments)}")
        
        if len(processor.segments) == 0:
            print("警告：没有生成线段数据")
            return
        
        # 检查线段数据
        print(f"\n前5个线段详情:")
        for i, segment in enumerate(processor.segments[:5]):
            direction_str = "向上" if segment.direction == 1 else "向下"
            print(f"线段{i}: {direction_str}, "
                  f"起点{segment.start_index}[{segment.start_price:.2f}] -> "
                  f"终点{segment.end_index}[{segment.end_price:.2f}]")
        
        # 创建可视化器进行简单测试
        visualizer = AdvancedChanlunVisualizer()
        
        # 准备结果字典
        result_dict = {
            "merged_df": processor.merged_df,
            "fractals": processor.fractals,
            "strokes": processor.strokes,
            "segments": processor.segments,
            "centrals": processor.centrals,
        }
        
        # 保存结果到CSV便于验证
        output_dir = "./test_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建线段数据摘要
        segments_summary = []
        for i, segment in enumerate(processor.segments):
            segments_summary.append({
                'segment_id': i,
                'direction': segment.direction,
                'start_index': segment.start_index,
                'end_index': segment.end_index,
                'start_price': segment.start_price,
                'end_price': segment.end_price,
                'length': segment.end_index - segment.start_index + 1,
                'price_change': abs(segment.end_price - segment.start_price)
            })
        
        summary_df = pd.DataFrame(segments_summary)
        summary_file = os.path.join(output_dir, f"{stock_code}_segments_summary.csv")
        summary_df.to_csv(summary_file, index=False)
        print(f"线段摘要已保存到: {summary_file}")
        
        # 绘制简单的测试图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        
        # 绘制K线图
        if hasattr(processor, 'merged_df') and processor.merged_df is not None:
            df = processor.merged_df
            ax1.plot(df.index, df['close'], label='Close Price', linewidth=1)
        else:
            ax1.plot(data.index, data['close'], label='Close Price', linewidth=1)
        
        # 绘制线段
        for i, segment in enumerate(processor.segments):
            color = 'green' if segment.direction == 1 else 'red'
            ax1.plot([segment.start_index, segment.end_index], 
                    [segment.start_price, segment.end_price], 
                    color=color, linewidth=3, alpha=0.7)
        
        ax1.set_title(f'{stock_code} 线段测试图')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 绘制笔
        for i, stroke in enumerate(processor.strokes[:50]):  # 只显示前50笔
            color = 'green' if stroke.direction == 1 else 'red'
            linestyle = '-' if len(processor.strokes) < 20 else ':'
            ax2.plot([stroke.start_index, stroke.end_index], 
                    [stroke.start_price, stroke.end_price], 
                    color=color, linewidth=1 if linestyle == ':' else 1.5, 
                    linestyle=linestyle)
        
        ax2.set_title(f'{stock_code} 笔测试图 (前{min(50, len(processor.strokes))}个)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        test_chart = os.path.join(output_dir, f"{stock_code}_segments_test.png")
        plt.savefig(test_chart, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"测试图表已保存到: {test_chart}")
        print("=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_segments_functionality()