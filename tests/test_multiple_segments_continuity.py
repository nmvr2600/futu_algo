#!/usr/bin/env python3
"""
测试复杂情况下的笔和线段连续性
验证在多个线段情况下笔和线段的连续性
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def create_complex_data_for_multiple_segments():
    """创建能生成多个线段的复杂数据"""
    data = []
    current_date = pd.Timestamp('2024-01-01')
    
    # 创建非常复杂的走势，确保能生成多个线段
    # 模式：上涨 -> 大幅回调 -> 上涨 -> 大幅回调 -> 上涨 -> 大幅回调 -> 上涨
    prices = []
    
    # 第一波上涨（20根K线）
    for i in range(20):
        prices.append(100 + i * 2.0)
    
    # 第一次大幅回调（15根K线）
    for i in range(15):
        prices.append(140 - i * 2.5)
    
    # 第二波上涨（18根K线）
    for i in range(18):
        prices.append(102.5 + i * 2.2)
    
    # 第二次大幅回调（16根K线）
    for i in range(16):
        prices.append(142.1 - i * 2.3)
    
    # 第三波上涨（20根K线）
    for i in range(20):
        prices.append(105.3 + i * 1.9)
    
    # 第三次大幅回调（15根K线）
    for i in range(15):
        prices.append(143.3 - i * 2.1)
    
    # 第四波上涨（18根K线）
    for i in range(18):
        prices.append(111.8 + i * 2.4)
    
    # 添加波动以形成分型
    for i, base_price in enumerate(prices):
        # 根据位置添加波动
        if i % 4 == 0:
            open_price = base_price - 0.5
            high_price = base_price + 1.0
            low_price = base_price - 1.0
            close_price = base_price + 0.3
        elif i % 4 == 1:
            open_price = base_price + 0.2
            high_price = base_price + 0.8
            low_price = base_price - 0.8
            close_price = base_price - 0.4
        elif i % 4 == 2:
            open_price = base_price - 0.3
            high_price = base_price + 1.2
            low_price = base_price - 1.2
            close_price = base_price + 0.6
        else:
            open_price = base_price + 0.1
            high_price = base_price + 0.6
            low_price = base_price - 0.6
            close_price = base_price - 0.2
            
        data.append({
            'time_key': current_date + pd.Timedelta(days=i),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000 + i * 10
        })
    
    return pd.DataFrame(data)


def test_multiple_segments_continuity():
    """测试多个线段的连续性"""
    print("=== 测试多个线段的连续性 ===")
    
    try:
        # 创建复杂测试数据
        df = create_complex_data_for_multiple_segments()
        print(f"测试数据长度: {len(df)}")
        
        # 处理数据
        processor = ChanlunProcessor()
        result = processor.process(df)
        
        # 获取数据
        strokes = result.get('strokes', [])
        segments = result.get('segments', [])
        print(f"生成的笔数量: {len(strokes)}")
        print(f"生成的线段数量: {len(segments)}")
        
        # 显示详细信息
        if len(strokes) > 0:
            print("\n前10个笔的详细信息:")
            for i, stroke in enumerate(strokes[:10]):
                direction_str = "上涨" if stroke.direction == 1 else "下跌"
                print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                      f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
                      f"索引 {stroke.start_index}->{stroke.end_index}")
        
        if len(segments) > 0:
            print("\n所有线段的详细信息:")
            for i, segment in enumerate(segments):
                direction_str = "上涨" if segment.direction == 1 else "下跌"
                print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
                      f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
                      f"索引 {segment.start_index}->{segment.end_index}")
        
        # 验证笔的连续性
        if len(strokes) >= 2:
            print("\n验证笔的连续性...")
            stroke_continuity_issues = []
            for i in range(1, len(strokes)):
                prev_stroke = strokes[i-1]
                curr_stroke = strokes[i]
                
                # 笔应该首尾相连
                if prev_stroke.end_index != curr_stroke.start_index:
                    stroke_continuity_issues.append({
                        'index': i,
                        'prev_end_index': prev_stroke.end_index,
                        'curr_start_index': curr_stroke.start_index,
                        'gap': curr_stroke.start_index - prev_stroke.end_index
                    })
                
                # 笔的方向应该交替
                if prev_stroke.direction == curr_stroke.direction:
                    stroke_continuity_issues.append({
                        'index': i,
                        'issue': 'direction_not_alternating',
                        'prev_direction': prev_stroke.direction,
                        'curr_direction': curr_stroke.direction
                    })
            
            if stroke_continuity_issues:
                print("❌ 笔连续性存在问题:")
                for issue in stroke_continuity_issues:
                    print(f"  {issue}")
                return False
            else:
                print("✅ 笔连续性测试通过")
        else:
            print("⚠️  笔数量不足，跳过笔连续性测试")
        
        # 验证线段的连续性
        if len(segments) >= 2:
            print("\n验证线段的连续性...")
            segment_continuity_issues = []
            for i in range(1, len(segments)):
                prev_segment = segments[i-1]
                curr_segment = segments[i]
                
                # 线段应该首尾相连（允许小的间隙）
                index_gap = curr_segment.start_index - prev_segment.end_index
                fractal_gap = curr_segment.fractal_start - prev_segment.fractal_end
                
                if index_gap > 3:  # 允许最多3个K线的间隙
                    segment_continuity_issues.append({
                        'index': i,
                        'type': 'index_gap_too_large',
                        'prev_end_index': prev_segment.end_index,
                        'curr_start_index': curr_segment.start_index,
                        'gap': index_gap
                    })
                
                if fractal_gap > 2:  # 允许最多2个分型的间隙
                    segment_continuity_issues.append({
                        'index': i,
                        'type': 'fractal_gap_too_large',
                        'prev_end_fractal': prev_segment.fractal_end,
                        'curr_start_fractal': curr_segment.fractal_start,
                        'gap': fractal_gap
                    })
            
            if segment_continuity_issues:
                print("❌ 线段连续性存在问题:")
                for issue in segment_continuity_issues:
                    print(f"  {issue}")
                return False
            else:
                print("✅ 线段连续性测试通过")
        elif len(segments) == 1:
            print("\n✅ 单个线段测试通过")
        else:
            print("\n⚠️  线段数量不足，跳过线段连续性测试")
        
        # 验证线段是否正确覆盖笔
        if len(strokes) >= 3 and len(segments) >= 1:
            print("\n验证线段覆盖...")
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
                print("❌ 线段覆盖存在问题:")
                for issue in coverage_issues:
                    print(f"  {issue}")
                return False
            else:
                print("✅ 线段覆盖测试通过")
        
        print("\n✅ 多线段连续性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 多线段连续性测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始运行多线段连续性测试...\n")
    
    success = test_multiple_segments_continuity()
    
    if success:
        print("\n🎉 多线段连续性测试通过！")
        return 0
    else:
        print("\n❌ 多线段连续性测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())