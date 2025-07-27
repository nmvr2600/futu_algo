#!/usr/bin/env python3
"""
演示线段破坏过程的详细示例
通过具体数据展示线段是如何被破坏并形成新线段的
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def create_segment_break_demonstration_data():
    """创建用于演示线段破坏的明确数据"""
    data = []
    current_date = pd.Timestamp('2024-01-01')
    
    # 创建一个明确的走势，能形成线段破坏
    prices = []
    
    # 明确的上涨线段构成
    # 第一波上涨：从100到130 (10根K线)
    for i in range(10):
        prices.append(100 + i * 3)
    
    # 小回调：从130到120 (5根K线)
    for i in range(5):
        prices.append(130 - i * 2)
    
    # 第二波上涨：从120到140 (7根K线)
    for i in range(7):
        prices.append(120 + i * 2.86)
    
    # 小回调：从140到130 (5根K线)
    for i in range(5):
        prices.append(140 - i * 2)
    
    # 第三波上涨：从130到150 (7根K线)
    for i in range(7):
        prices.append(130 + i * 2.86)
    
    # 破坏性下跌：从150到110 (15根K线) - 足够破坏上涨线段
    for i in range(15):
        prices.append(150 - i * 2.67)
    
    # 明确的下跌线段构成
    # 第一波下跌：从110到90 (10根K线)
    for i in range(10):
        prices.append(110 - i * 2)
    
    # 小反弹：从90到95 (3根K线)
    for i in range(3):
        prices.append(90 + i * 1.67)
    
    # 第二波下跌：从95到75 (10根K线)
    for i in range(10):
        prices.append(95 - i * 2)
    
    # 破坏性上涨：从75到105 (12根K线) - 足够破坏下跌线段
    for i in range(12):
        prices.append(75 + i * 2.5)
    
    # 新的上涨线段
    # 上涨：从105到120 (6根K线)
    for i in range(6):
        prices.append(105 + i * 2.5)
    
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


def demonstrate_segment_break_process():
    """演示线段破坏过程"""
    print("=== 线段破坏过程演示 ===")
    
    # 创建演示数据
    df = create_segment_break_demonstration_data()
    print(f"演示数据长度: {len(df)}")
    
    # 处理数据
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    # 获取详细信息
    fractals = result.get('fractals', [])
    strokes = result.get('strokes', [])
    segments = result.get('segments', [])
    
    print(f"\n识别到的分型数量: {len(fractals)}")
    print("分型详情:")
    for i, fractal in enumerate(fractals[:10]):  # 只显示前10个
        type_str = "顶" if fractal.type.value == "top" else "底"
        print(f"  分型 {fractal.idx}: {type_str}分型, 索引={fractal.index}, 价格={fractal.price:.2f}")
    if len(fractals) > 10:
        print(f"  ... 还有 {len(fractals) - 10} 个分型")
    
    print(f"\n构建的笔数量: {len(strokes)}")
    print("笔详情:")
    for i, stroke in enumerate(strokes[:15]):  # 只显示前15个
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
              f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
              f"索引 {stroke.start_index}->{stroke.end_index}")
    if len(strokes) > 15:
        print(f"  ... 还有 {len(strokes) - 15} 个笔")
    
    print(f"\n构建的线段数量: {len(segments)}")
    print("线段详情:")
    for i, segment in enumerate(segments):
        direction_str = "上涨" if segment.direction == 1 else "下跌"
        print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
              f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
              f"索引 {segment.start_index}->{segment.end_index}")
    
    # 详细分析线段破坏过程
    print("\n=== 线段破坏详细过程 ===")
    
    if len(segments) >= 2:
        print("检测到线段破坏过程:")
        for i in range(len(segments)):
            segment = segments[i]
            direction_str = "上涨" if segment.direction == 1 else "下跌"
            print(f"\n线段 {segment.idx} ({direction_str}):")
            print(f"  起点: 分型{segment.fractal_start}, 价格{segment.start_price:.2f}")
            print(f"  终点: 分型{segment.fractal_end}, 价格{segment.end_price:.2f}")
            print(f"  索引范围: {segment.start_index} -> {segment.end_index}")
            
            if i > 0:
                prev_segment = segments[i-1]
                prev_direction_str = "上涨" if prev_segment.direction == 1 else "下跌"
                print(f"  前一线段: {prev_direction_str} ({prev_segment.start_price:.2f} -> {prev_segment.end_price:.2f})")
                
                # 分析破坏过程
                if prev_segment.direction != segment.direction:
                    print(f"  ✅ 线段方向发生转变: {prev_direction_str} -> {direction_str}")
                    
                    # 查找破坏点
                    break_point = None
                    for stroke in strokes:
                        if (stroke.start_index >= prev_segment.end_index and 
                            stroke.start_index <= segment.start_index):
                            break_point = stroke
                            break
                    
                    if break_point:
                        break_direction_str = "上涨" if break_point.direction == 1 else "下跌"
                        print(f"  破坏笔: 笔{break_point.idx} ({break_direction_str}), "
                              f"索引 {break_point.start_index} -> {break_point.end_index}")
                else:
                    print(f"  ⚠️  线段方向未发生转变")
    else:
        print("未检测到明显的线段破坏（只有单个线段或无线段）")
        
        if len(segments) == 1:
            segment = segments[0]
            direction_str = "上涨" if segment.direction == 1 else "下跌"
            print(f"单个线段: {direction_str}")
            print(f"  覆盖范围: 价格 {segment.start_price:.2f} -> {segment.end_price:.2f}")
            print(f"  索引范围: {segment.start_index} -> {segment.end_index}")
            
            # 分析线段构成
            segment_strokes = [s for s in strokes 
                             if s.start_index >= segment.start_index and s.end_index <= segment.end_index]
            print(f"  包含笔数: {len(segment_strokes)}")
            
            # 按方向分组
            up_strokes = [s for s in segment_strokes if s.direction == 1]
            down_strokes = [s for s in segment_strokes if s.direction == -1]
            print(f"  上涨笔: {len(up_strokes)}, 下跌笔: {len(down_strokes)}")
    
    print("\n=== 线段破坏判断逻辑 ===")
    print("1. 线段形成条件:")
    print("   - 至少3笔")
    print("   - 前三笔有价格重叠")
    print("   - 笔方向交替 (如: 下跌->上涨->下跌)")
    print("   - 线段方向由第一笔决定")
    
    print("\n2. 线段破坏条件:")
    print("   - 出现足够强的反向笔")
    print("   - 反向笔终点突破原线段最后一笔的极值点")
    print("   - 反向笔完成后有延续走势")
    
    print("\n3. 新线段形成:")
    print("   - 破坏点成为新线段的起点")
    print("   - 新线段方向与原线段相反")
    print("   - 新线段需满足形成条件")
    
    # 分析当前数据是否满足线段破坏条件
    if len(strokes) >= 6:
        print("\n=== 当前走势分析 ===")
        # 查找可能的破坏模式
        for i in range(len(strokes) - 3):
            stroke1 = strokes[i]
            stroke2 = strokes[i + 1]
            stroke3 = strokes[i + 2]
            stroke4 = strokes[i + 3]
            
            # 检查是否为破坏模式: 同向->反向->同向->强反向
            if (stroke1.direction == stroke3.direction and 
                stroke1.direction != stroke2.direction and
                stroke2.direction == stroke4.direction and
                abs(stroke4.end_price - stroke4.start_price) > abs(stroke2.end_price - stroke2.start_price) * 1.5):
                
                direction1_str = "上涨" if stroke1.direction == 1 else "下跌"
                direction2_str = "上涨" if stroke2.direction == 1 else "下跌"
                direction4_str = "上涨" if stroke4.direction == 1 else "下跌"
                
                print(f"  潜在破坏模式在笔 {stroke1.idx}-{stroke4.idx}:")
                print(f"    {direction1_str} -> {direction2_str} -> {direction1_str} -> {direction4_str} (强力{direction4_str})")
                print(f"    破坏笔 {stroke4.idx}: 价格变动 {abs(stroke4.end_price - stroke4.start_price):.2f}")


def main():
    """主演示函数"""
    print("🚀 开始线段破坏过程演示...\n")
    
    demonstrate_segment_break_process()
    
    print("\n🎉 线段破坏过程演示完成！")


if __name__ == "__main__":
    main()