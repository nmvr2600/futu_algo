#!/usr/bin/env python3
"""
测试线段构建问题
验证为什么现在每张图都只有一根线段
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def create_clear_segment_break_data():
    """创建能明确显示线段破坏的数据"""
    data = []
    current_date = pd.Timestamp('2024-01-01')
    
    # 创建明确的走势：上涨线段 -> 破坏性下跌 -> 下跌线段 -> 破坏性上涨 -> 上涨线段
    prices = []
    
    print("创建明确的多线段走势数据...")
    
    # 第一个明确的上涨线段
    print("1. 第一个上涨线段")
    # 上涨1: 从100到120 (8根K线)
    for i in range(8):
        prices.append(100 + i * 2.5)
    print(f"   上涨1: 100 -> 120 (8根K线)")
    
    # 小回调1: 从120到110 (4根K线)
    for i in range(4):
        prices.append(120 - i * 2.5)
    print(f"   回调1: 120 -> 110 (4根K线)")
    
    # 上涨2: 从110到130 (8根K线)
    for i in range(8):
        prices.append(110 + i * 2.5)
    print(f"   上涨2: 110 -> 130 (8根K线)")
    
    # 小回调2: 从130到120 (4根K线)
    for i in range(4):
        prices.append(130 - i * 2.5)
    print(f"   回调2: 130 -> 120 (4根K线)")
    
    # 上涨3: 从120到140 (8根K线)
    for i in range(8):
        prices.append(120 + i * 2.5)
    print(f"   上涨3: 120 -> 140 (8根K线)")
    
    # 破坏性下跌：从140到90 (20根K线) - 足够破坏上涨线段
    print("\n2. 破坏性下跌")
    for i in range(20):
        prices.append(140 - i * 2.5)
    print(f"   破坏下跌: 140 -> 90 (20根K线)")
    
    # 第二个明确的下跌线段
    print("\n3. 第二个下跌线段")
    # 下跌1: 从90到70 (8根K线)
    for i in range(8):
        prices.append(90 - i * 2.5)
    print(f"   下跌1: 90 -> 70 (8根K线)")
    
    # 小反弹1: 从70到80 (4根K线)
    for i in range(4):
        prices.append(70 + i * 2.5)
    print(f"   反弹1: 70 -> 80 (4根K线)")
    
    # 下跌2: 从80到60 (8根K线)
    for i in range(8):
        prices.append(80 - i * 2.5)
    print(f"   下跌2: 80 -> 60 (8根K线)")
    
    # 小反弹2: 从60到70 (4根K线)
    for i in range(4):
        prices.append(60 + i * 2.5)
    print(f"   反弹2: 60 -> 70 (4根K线)")
    
    # 下跌3: 从70到50 (8根K线)
    for i in range(8):
        prices.append(70 - i * 2.5)
    print(f"   下跌3: 70 -> 50 (8根K线)")
    
    # 破坏性上涨：从50到100 (20根K线) - 足够破坏下跌线段
    print("\n4. 破坏性上涨")
    for i in range(20):
        prices.append(50 + i * 2.5)
    print(f"   破坏上涨: 50 -> 100 (20根K线)")
    
    # 第三个明确的上涨线段
    print("\n5. 第三个上涨线段")
    # 上涨1: 从100到115 (6根K线)
    for i in range(6):
        prices.append(100 + i * 2.5)
    print(f"   上涨1: 100 -> 115 (6根K线)")
    
    # 小回调1: 从115到105 (4根K线)
    for i in range(4):
        prices.append(115 - i * 2.5)
    print(f"   回调1: 115 -> 105 (4根K线)")
    
    # 上涨2: 从105到120 (6根K线)
    for i in range(6):
        prices.append(105 + i * 2.5)
    print(f"   上涨2: 105 -> 120 (6根K线)")
    
    print(f"\n总计: {len(prices)} 根K线")
    
    # 添加波动以形成分型
    for i, base_price in enumerate(prices):
        # 根据位置添加波动
        if i % 3 == 0:
            open_price = base_price - 0.4
            high_price = base_price + 0.8
            low_price = base_price - 0.8
            close_price = base_price + 0.3
        elif i % 3 == 1:
            open_price = base_price + 0.2
            high_price = base_price + 0.6
            low_price = base_price - 0.6
            close_price = base_price - 0.2
        else:
            open_price = base_price - 0.3
            high_price = base_price + 0.7
            low_price = base_price - 0.7
            close_price = base_price + 0.2
            
        data.append({
            'time_key': current_date + pd.Timedelta(days=i),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000 + i * 10
        })
    
    return pd.DataFrame(data)


def debug_segment_construction():
    """调试线段构建问题"""
    print("=== 调试线段构建问题 ===")
    
    # 创建测试数据
    df = create_clear_segment_break_data()
    print(f"\n测试数据长度: {len(df)}")
    
    # 处理数据
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    # 获取详细信息
    fractals = result.get('fractals', [])
    strokes = result.get('strokes', [])
    segments = result.get('segments', [])
    centrals = result.get('centrals', [])
    
    print(f"\n识别到的分型数量: {len(fractals)}")
    print("分型详情:")
    for i, fractal in enumerate(fractals[:15]):  # 只显示前15个
        type_str = "顶" if fractal.type.value == "top" else "底"
        print(f"  分型 {fractal.idx}: {type_str}分型, 索引={fractal.index}, 价格={fractal.price:.2f}")
    if len(fractals) > 15:
        print(f"  ... 还有 {len(fractals) - 15} 个分型")
    
    print(f"\n构建的笔数量: {len(strokes)}")
    print("笔详情:")
    for i, stroke in enumerate(strokes[:20]):  # 只显示前20个
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
              f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
              f"索引 {stroke.start_index}->{stroke.end_index}")
    if len(strokes) > 20:
        print(f"  ... 还有 {len(strokes) - 20} 个笔")
    
    print(f"\n构建的线段数量: {len(segments)}")
    print("线段详情:")
    for i, segment in enumerate(segments):
        direction_str = "上涨" if segment.direction == 1 else "下跌"
        print(f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
              f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
              f"索引 {segment.start_index}->{segment.end_index}")
    
    print(f"\n构建的中枢数量: {len(centrals)}")
    print("中枢详情:")
    for i, central in enumerate(centrals):
        print(f"  中枢 {i+1}: 价格区间=[{central.low:.2f}, {central.high:.2f}], "
              f"索引 {central.start_index}->{central.end_index}")
    
    # 详细分析线段构建过程
    print("\n=== 详细分析线段构建过程 ===")
    
    if len(strokes) >= 3:
        print("1. 检查所有可能的线段起点:")
        
        # 手动检查每个可能的起点
        for i in range(min(len(strokes) - 2, 10)):  # 只检查前10个可能的起点
            stroke1 = strokes[i]
            stroke2 = strokes[i + 1]
            stroke3 = strokes[i + 2]
            
            print(f"\n   检查起点 {i} (笔{stroke1.idx}, {stroke2.idx}, {stroke3.idx}):")
            direction1_str = "上涨" if stroke1.direction == 1 else "下跌"
            direction2_str = "上涨" if stroke2.direction == 1 else "下跌"
            direction3_str = "上涨" if stroke3.direction == 1 else "下跌"
            print(f"     笔{stroke1.idx}: {direction1_str} {stroke1.start_price:.2f}->{stroke1.end_price:.2f}")
            print(f"     笔{stroke2.idx}: {direction2_str} {stroke2.start_price:.2f}->{stroke2.end_price:.2f}")
            print(f"     笔{stroke3.idx}: {direction3_str} {stroke3.start_price:.2f}->{stroke3.end_price:.2f}")
            
            # 检查方向交替性
            direction_ok = (stroke1.direction == stroke3.direction and 
                           stroke1.direction != stroke2.direction)
            print(f"     方向交替性: {'✅ 满足' if direction_ok else '❌ 不满足'}")
            
            if direction_ok:
                # 计算价格区间
                if stroke1.direction == 1:  # 向上笔
                    range1 = (stroke1.start_price, stroke1.end_price)
                    range2 = (stroke2.end_price, stroke2.start_price)  # 下跌笔，区间反转
                    range3 = (stroke3.start_price, stroke3.end_price)
                else:  # 向下笔
                    range1 = (stroke1.end_price, stroke1.start_price)
                    range2 = (stroke2.start_price, stroke2.end_price)
                    range3 = (stroke3.end_price, stroke3.start_price)
                
                print(f"     价格区间: range1={range1}, range2={range2}, range3={range3}")
                
                # 计算重叠区间
                overlap_low = max(min(range1), min(range2), min(range3))
                overlap_high = min(max(range1), max(range2), max(range3))
                has_overlap = overlap_low <= overlap_high
                
                print(f"     重叠区间: [{overlap_low:.2f}, {overlap_high:.2f}] - "
                      f"{'✅ 有重叠' if has_overlap else '❌ 无重叠'}")
                
                if has_overlap:
                    print(f"     ✅ 起点 {i} 满足条件，可以形成线段!")
                else:
                    print(f"     ❌ 起点 {i} 不满足重叠条件")
            else:
                print(f"     ❌ 起点 {i} 不满足方向交替条件")
    
    print("\n2. 分析为什么只生成了一个线段:")
    
    if len(segments) == 1 and len(strokes) > 3:
        segment = segments[0]
        print(f"   单个线段覆盖了从笔{segment.fractal_start}到笔{segment.fractal_end}")
        print(f"   线段方向: {'上涨' if segment.direction == 1 else '下跌'}")
        
        # 检查是否是因为默认处理逻辑
        # 查看是否所有笔都是同向的
        up_strokes = [s for s in strokes if s.direction == 1]
        down_strokes = [s for s in strokes if s.direction == -1]
        print(f"   上涨笔数量: {len(up_strokes)}, 下跌笔数量: {len(down_strokes)}")
        
        if len(up_strokes) > len(down_strokes):
            dominant_direction = "上涨"
            dominant_count = len(up_strokes)
        else:
            dominant_direction = "下跌"
            dominant_count = len(down_strokes)
        
        print(f"   主导方向: {dominant_direction} (数量: {dominant_count})")
        print(f"   线段方向: {'上涨' if segment.direction == 1 else '下跌'}")
        
        if (dominant_direction == "上涨" and segment.direction == 1) or \
           (dominant_direction == "下跌" and segment.direction == -1):
            print("   ⚠️  可能是默认处理逻辑：将所有笔合并为一个线段")
    
    print("\n3. 对比中枢构建:")
    print(f"   中枢数量: {len(centrals)}")
    print(f"   线段数量: {len(segments)}")
    
    if len(centrals) > 1 and len(segments) == 1:
        print("   ❌ 问题确认: 有多个中枢但只有一个线段")
        print("   这表明线段破坏逻辑没有正确实现")
    
    # 分析中枢构成
    if len(centrals) > 0:
        print("\n4. 中枢构成分析:")
        for i, central in enumerate(centrals):
            if central.strokes:
                print(f"   中枢 {i+1} 由 {len(central.strokes)} 笔构成:")
                for j, stroke in enumerate(central.strokes):
                    direction_str = "上涨" if stroke.direction == 1 else "下跌"
                    print(f"     笔{stroke.idx}: {direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}")


def main():
    """主调试函数"""
    print("🚀 开始调试线段构建问题...\n")
    
    debug_segment_construction()
    
    print("\n🔍 调试完成！")


if __name__ == "__main__":
    main()