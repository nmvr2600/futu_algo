#!/usr/bin/env python3
"""
演示线段判断过程的详细示例
通过具体数据展示线段是如何判断和构建的
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def create_demonstration_data():
    """创建用于演示线段判断的明确数据"""
    data = []
    current_date = pd.Timestamp('2024-01-01')
    
    # 创建一个明确的走势，能形成清晰的线段
    prices = []
    
    # 第一波上涨趋势（形成多个上涨笔）
    # 上涨1: 从100到110 (5根K线)
    for i in range(5):
        prices.append(100 + i * 2)
    
    # 回调1: 从110到105 (3根K线)
    for i in range(3):
        prices.append(110 - i * 1.67)
    
    # 上涨2: 从105到115 (5根K线)
    for i in range(5):
        prices.append(105 + i * 2)
    
    # 回调2: 从115到108 (4根K线)
    for i in range(4):
        prices.append(115 - i * 1.75)
    
    # 上涨3: 从108到118 (5根K线)
    for i in range(5):
        prices.append(108 + i * 2)
    
    # 破坏性下跌（形成线段破坏）
    # 从118下跌到100 (6根K线)
    for i in range(6):
        prices.append(118 - i * 3)
    
    # 新的下跌趋势
    # 下跌1: 从100到95 (3根K线)
    for i in range(3):
        prices.append(100 - i * 1.67)
    
    # 小反弹: 从95到98 (2根K线)
    for i in range(2):
        prices.append(95 + i * 1.5)
    
    # 下跌2: 从98到90 (4根K线)
    for i in range(4):
        prices.append(98 - i * 2)
    
    # 添加波动以形成分型
    for i, base_price in enumerate(prices):
        # 根据位置添加波动
        if i % 3 == 0:
            open_price = base_price - 0.3
            high_price = base_price + 0.5
            low_price = base_price - 0.5
            close_price = base_price + 0.2
        elif i % 3 == 1:
            open_price = base_price + 0.1
            high_price = base_price + 0.3
            low_price = base_price - 0.3
            close_price = base_price - 0.1
        else:
            open_price = base_price - 0.2
            high_price = base_price + 0.4
            low_price = base_price - 0.4
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


def demonstrate_segment_judgment():
    """演示线段判断过程"""
    print("=== 线段判断过程演示 ===")
    
    # 创建演示数据
    df = create_demonstration_data()
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
    for i, fractal in enumerate(fractals):
        type_str = "顶" if fractal.type.value == "top" else "底"
        print(f"  分型 {fractal.idx}: {type_str}分型, 索引={fractal.index}, 价格={fractal.price:.2f}")
    
    print(f"\n构建的笔数量: {len(strokes)}")
    print("笔详情:")
    for i, stroke in enumerate(strokes):
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
              f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
              f"索引 {stroke.start_index}->{stroke.end_index}")
    
    print(f"\n构建的线段数量: {len(segments)}")
    print("线段详情:")
    for i, segment in enumerate(segments):
        direction_str = "上涨" if segment.direction == 1 else "下跌"
        print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
              f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
              f"索引 {segment.start_index}->{segment.end_index}")
    
    # 详细分析线段判断过程
    print("\n=== 线段判断详细过程 ===")
    
    if len(strokes) >= 3:
        print("1. 检查笔数量:")
        print(f"   笔数量: {len(strokes)} (要求 >= 3) - {'✅ 满足' if len(strokes) >= 3 else '❌ 不满足'}")
        
        print("\n2. 寻找线段起点 (前三笔满足条件):")
        for i in range(len(strokes) - 2):
            stroke1 = strokes[i]
            stroke2 = strokes[i + 1]
            stroke3 = strokes[i + 2]
            
            print(f"\n   检查起点 {i}:")
            print(f"   笔{i+1}: 方向={'上涨' if stroke1.direction == 1 else '下跌'}, "
                  f"价格区间=[{stroke1.start_price:.2f}, {stroke1.end_price:.2f}]")
            print(f"   笔{i+2}: 方向={'上涨' if stroke2.direction == 1 else '下跌'}, "
                  f"价格区间=[{stroke2.start_price:.2f}, {stroke2.end_price:.2f}]")
            print(f"   笔{i+3}: 方向={'上涨' if stroke3.direction == 1 else '下跌'}, "
                  f"价格区间=[{stroke3.start_price:.2f}, {stroke3.end_price:.2f}]")
            
            # 检查方向交替性
            direction_ok = (stroke1.direction == stroke3.direction and 
                           stroke1.direction != stroke2.direction)
            print(f"   方向交替性检查: 第1笔和第3笔{'同向' if stroke1.direction == stroke3.direction else '异向'}, "
                  f"第1笔和第2笔{'同向' if stroke1.direction == stroke2.direction else '异向'} - "
                  f"{'✅ 满足' if direction_ok else '❌ 不满足'}")
            
            if direction_ok:
                # 计算价格区间重叠
                if stroke1.direction == 1:  # 向上笔
                    range1 = (stroke1.start_price, stroke1.end_price)
                    range2 = (stroke2.end_price, stroke2.start_price)  # 向下笔，区间反转
                    range3 = (stroke3.start_price, stroke3.end_price)
                else:  # 向下笔
                    range1 = (stroke1.end_price, stroke1.start_price)
                    range2 = (stroke2.start_price, stroke2.end_price)
                    range3 = (stroke3.end_price, stroke3.start_price)
                
                overlap_low = max(min(range1), min(range2), min(range3))
                overlap_high = min(max(range1), max(range2), max(range3))
                has_overlap = overlap_low <= overlap_high
                
                print(f"   价格区间: range1={range1}, range2={range2}, range3={range3}")
                print(f"   重叠区间: [{overlap_low:.2f}, {overlap_high:.2f}] - "
                      f"{'✅ 有重叠' if has_overlap else '❌ 无重叠'}")
                
                if has_overlap:
                    print(f"   ✅ 起点 {i} 满足条件，可以形成线段!")
                    break
                else:
                    print(f"   ❌ 起点 {i} 不满足重叠条件")
            else:
                print(f"   ❌ 起点 {i} 不满足方向交替条件")
    
    print("\n3. 线段生长过程:")
    if len(segments) > 0:
        segment = segments[0]
        print(f"   线段方向: {'上涨' if segment.direction == 1 else '下跌'}")
        print(f"   从笔 {segment.fractal_start} 开始，到笔 {segment.fractal_end} 结束")
        print(f"   包含所有同向的连续笔")
        
        # 显示同向笔
        same_direction_strokes = [s for s in strokes if s.direction == segment.direction]
        print(f"   同向笔数量: {len(same_direction_strokes)}")
        for i, stroke in enumerate(same_direction_strokes):
            print(f"     笔 {stroke.idx}: {'上涨' if stroke.direction == 1 else '下跌'}")
    
    print("\n4. 线段破坏判断:")
    print("   线段破坏条件:")
    print("   - 出现足够强的反向笔，其终点突破线段最后同向笔的极值点")
    print("   - 反向笔完成后，必须有至少一笔延续走势")
    
    # 如果有多于一个线段，说明发生了破坏
    if len(segments) >= 2:
        print("   ✅ 检测到线段破坏，形成了多个线段")
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            print(f"   线段{i} ({'上涨' if prev_segment.direction == 1 else '下跌'}) -> "
                  f"线段{i+1} ({'上涨' if curr_segment.direction == 1 else '下跌'})")
    else:
        print("   ⚠️  未检测到线段破坏（可能因为数据不足或趋势未结束）")
    
    print("\n=== 总结 ===")
    print(f"最终结果: 生成了 {len(segments)} 个线段")
    if len(segments) == 1:
        print("线段特征: 单个线段覆盖了大部分同向笔")
    elif len(segments) > 1:
        print("线段特征: 多个线段表示趋势发生了破坏和转换")
    else:
        print("线段特征: 未生成线段（可能笔数量不足或不满足条件）")


def main():
    """主演示函数"""
    print("🚀 开始线段判断过程演示...\n")
    
    demonstrate_segment_judgment()
    
    print("\n🎉 线段判断过程演示完成！")


if __name__ == "__main__":
    main()