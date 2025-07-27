#!/usr/bin/env python3
"""
测试线段破坏条件和连续性
验证线段在遇到破坏时的正确行为
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def create_data_with_segment_break():
    """创建能明确显示线段破坏的数据"""
    data = []
    current_date = pd.Timestamp('2024-01-01')
    
    # 创建明确的线段破坏模式
    # 模式：上涨线段 -> 破坏性下跌 -> 新的下跌线段 -> 破坏性上涨 -> 新的上涨线段
    prices = []
    
    # 第一个上涨线段的构成（多个小上涨和小回调）
    # 上涨1
    for i in range(5):
        prices.append(100 + i * 1.5)
    # 小回调1
    for i in range(3):
        prices.append(107.5 - i * 0.8)
    # 上涨2
    for i in range(6):
        prices.append(105.1 + i * 1.8)
    # 小回调2
    for i in range(4):
        prices.append(115.9 - i * 1.2)
    # 上涨3
    for i in range(5):
        prices.append(111.1 + i * 1.6)
    
    # 破坏性下跌（足够大以破坏上涨线段）
    for i in range(8):
        prices.append(119.1 - i * 3.0)
    
    # 新的下跌线段
    # 下跌1
    for i in range(4):
        prices.append(95.1 - i * 1.2)
    # 小反弹1
    for i in range(2):
        prices.append(90.3 + i * 0.9)
    # 下跌2
    for i in range(5):
        prices.append(92.1 - i * 1.4)
    # 小反弹2
    for i in range(3):
        prices.append(85.1 + i * 0.7)
    # 下跌3
    for i in range(4):
        prices.append(87.2 - i * 1.3)
    
    # 破坏性上涨（足够大以破坏下跌线段）
    for i in range(10):
        prices.append(81.0 + i * 2.5)
    
    # 新的上涨线段
    # 上涨1
    for i in range(3):
        prices.append(106.0 + i * 1.2)
    # 小回调1
    for i in range(2):
        prices.append(109.6 - i * 0.8)
    # 上涨2
    for i in range(4):
        prices.append(108.0 + i * 1.5)
    
    # 添加波动以形成分型
    for i, base_price in enumerate(prices):
        # 根据位置添加波动
        if i % 3 == 0:
            open_price = base_price - 0.3
            high_price = base_price + 0.6
            low_price = base_price - 0.6
            close_price = base_price + 0.2
        elif i % 3 == 1:
            open_price = base_price + 0.1
            high_price = base_price + 0.4
            low_price = base_price - 0.4
            close_price = base_price - 0.2
        else:
            open_price = base_price - 0.2
            high_price = base_price + 0.5
            low_price = base_price - 0.5
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


def test_segment_break_and_continuity():
    """测试线段破坏和连续性"""
    print("=== 测试线段破坏和连续性 ===")
    
    try:
        # 创建测试数据
        df = create_data_with_segment_break()
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
            print("\n前15个笔的详细信息:")
            for i, stroke in enumerate(strokes[:15]):
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
        else:
            print("\n⚠️  未生成线段")
            # 显示所有笔，帮助分析原因
            print("显示所有笔以分析线段构建问题:")
            for i, stroke in enumerate(strokes):
                direction_str = "上涨" if stroke.direction == 1 else "下跌"
                print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                      f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}")
        
        # 验证线段破坏逻辑
        if len(segments) >= 2:
            print("\n验证线段破坏逻辑...")
            break_issues = []
            
            # 检查相邻线段的方向是否交替（符合破坏逻辑）
            for i in range(1, len(segments)):
                prev_segment = segments[i-1]
                curr_segment = segments[i]
                
                # 线段方向应该交替（上涨->下跌->上涨 或 下跌->上涨->下跌）
                if prev_segment.direction == curr_segment.direction:
                    break_issues.append({
                        'index': i,
                        'issue': 'direction_not_alternating_after_break',
                        'prev_direction': prev_segment.direction,
                        'curr_direction': curr_segment.direction
                    })
            
            if break_issues:
                print("❌ 线段破坏逻辑存在问题:")
                for issue in break_issues:
                    direction_str = lambda d: "上涨" if d == 1 else "下跌"
                    print(f"  线段{i-1}({direction_str(issue['prev_direction'])}) 和 线段{i}({direction_str(issue['curr_direction'])}) 方向相同")
                return False
            else:
                print("✅ 线段破坏逻辑测试通过")
        elif len(segments) == 1:
            print("\n✅ 单个线段测试通过")
        else:
            print("\n⚠️  线段数量不足，无法验证破坏逻辑")
        
        # 验证线段连续性（即使有破坏，线段也应该连续）
        if len(segments) >= 2:
            print("\n验证线段连续性...")
            continuity_issues = []
            
            for i in range(1, len(segments)):
                prev_segment = segments[i-1]
                curr_segment = segments[i]
                
                # 检查线段是否连续（终点应该等于起点）
                if prev_segment.end_index != curr_segment.start_index:
                    # 允许小的间隙
                    gap = curr_segment.start_index - prev_segment.end_index
                    if gap > 2:  # 最多允许2个K线的间隙
                        continuity_issues.append({
                            'index': i,
                            'type': 'index_not_continuous',
                            'prev_end_index': prev_segment.end_index,
                            'curr_start_index': curr_segment.start_index,
                            'gap': gap
                        })
                
                if prev_segment.fractal_end != curr_segment.fractal_start:
                    # 允许小的分型间隙
                    fractal_gap = curr_segment.fractal_start - prev_segment.fractal_end
                    if fractal_gap > 1:  # 最多允许1个分型的间隙
                        continuity_issues.append({
                            'index': i,
                            'type': 'fractal_not_continuous',
                            'prev_end_fractal': prev_segment.fractal_end,
                            'curr_start_fractal': curr_segment.fractal_start,
                            'gap': fractal_gap
                        })
            
            if continuity_issues:
                print("❌ 线段连续性存在问题:")
                for issue in continuity_issues:
                    print(f"  {issue}")
                return False
            else:
                print("✅ 线段连续性测试通过")
        
        # 验证笔和线段的一致性
        if len(strokes) > 0 and len(segments) > 0:
            print("\n验证笔和线段一致性...")
            consistency_issues = []
            
            # 第一个线段的起点应该与第一个笔的起点一致（或接近）
            first_stroke = strokes[0]
            first_segment = segments[0]
            
            if abs(first_segment.start_index - first_stroke.start_index) > 2:
                consistency_issues.append({
                    'type': 'first_segment_stroke_mismatch',
                    'segment_start': first_segment.start_index,
                    'stroke_start': first_stroke.start_index
                })
            
            # 最后一个线段的终点应该与最后一个笔的终点一致（或接近）
            last_stroke = strokes[-1]
            last_segment = segments[-1]
            
            if abs(last_segment.end_index - last_stroke.end_index) > 2:
                consistency_issues.append({
                    'type': 'last_segment_stroke_mismatch',
                    'segment_end': last_segment.end_index,
                    'stroke_end': last_stroke.end_index
                })
            
            if consistency_issues:
                print("❌ 笔和线段一致性存在问题:")
                for issue in consistency_issues:
                    print(f"  {issue}")
                return False
            else:
                print("✅ 笔和线段一致性测试通过")
        
        print("\n✅ 线段破坏和连续性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 线段破坏和连续性测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始运行线段破坏和连续性测试...\n")
    
    success = test_segment_break_and_continuity()
    
    if success:
        print("\n🎉 线段破坏和连续性测试通过！")
        return 0
    else:
        print("\n❌ 线段破坏和连续性测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    exit(main())