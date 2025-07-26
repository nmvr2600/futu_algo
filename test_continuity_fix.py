#!/usr/bin/env python3
"""
线段连续性修复验证脚本
使用测试数据验证线段不再断裂
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from util.chanlun import ChanlunProcessor

def create_test_data():
    """创建用于验证线段连续性的测试数据"""
    base_time = datetime.now()
    data = []
    
    # 创建一个确保产生多个线段的复杂模式
    # 上涨段
    prices = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]
    for i, price in enumerate(prices):
        data.append({
            'time_key': base_time + timedelta(hours=i),
            'open': price - 1,
            'high': price + 1,
            'low': price - 2,
            'close': price,
            'volume': 1000 + i * 100
        })
    
    # 下跌段
    prices = [118, 115, 112, 109, 106, 103, 100, 97, 94, 91]
    for i, price in enumerate(prices):
        data.append({
            'time_key': base_time + timedelta(hours=10+i),
            'open': price - 1,
            'high': price + 1,
            'low': price - 2,
            'close': price,
            'volume': 1000 + i * 100
        })
    
    # 上涨段
    prices = [91, 94, 97, 100, 103, 106, 109, 112, 115, 118]
    for i, price in enumerate(prices):
        data.append({
            'time_key': base_time + timedelta(hours=20+i),
            'open': price - 1,
            'high': price + 1,
            'low': price - 2,
            'close': price,
            'volume': 1000 + i * 100
        })
    
    return data

def verify_segment_continuity(segments):
    """验证线段连续性"""
    if len(segments) < 2:
        print("✅ 只有1个线段，不存在断裂问题")
        return True
    
    print(f"\n📊 验证{len(segments)}个线段的连续性...")
    
    for i in range(1, len(segments)):
        prev = segments[i-1]
        curr = segments[i]
        
        # 检查索引连续性
        index_gap = curr.start_index - prev.end_index
        
        # 检查分形连续性
        fractal_gap = curr.fractal_start - prev.fractal_end
        
        print(f"线段{i-1} → 线段{i}:")
        print(f"  索引范围: [{prev.start_index},{prev.end_index}] → [{curr.start_index},{curr.end_index}]")
        print(f"  分形范围: [{prev.fractal_start},{prev.fractal_end}] → [{curr.fractal_start},{curr.fractal_end}]")
        print(f"  索引间隙: {index_gap}")
        print(f"  分形间隙: {fractal_gap}")
        
        # 允许最多1个单位的间隙（由于分型对齐）
        if index_gap <= 1 and fractal_gap <= 1:
            print("  ✅ 连续性良好")
        else:
            print(f"  ❌ 发现断裂！索引间隙={index_gap}, 分形间隙={fractal_gap}")
            return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 线段连续性修复验证")
    print("=" * 50)
    
    # 创建测试数据
    test_data = create_test_data()
    print(f"📈 创建测试数据: {len(test_data)}根K线")
    
    # 处理数据
    import pandas as pd
    df = pd.DataFrame(test_data)
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    # 显示结果
    print(f"\n📊 分析结果:")
    print(f"  分型数量: {len(result['fractals'])}")
    print(f"  笔数量: {len(result['strokes'])}")
    print(f"  线段数量: {len(result['segments'])}")
    
    # 详细显示线段
    if result['segments']:
        print("\n🎯 线段详情:")
        for i, segment in enumerate(result['segments']):
            print(f"  线段{i+1}: [{segment.start_index}-{segment.end_index}] "
                  f"方向={'↑' if segment.direction == 1 else '↓'} "
                  f"价格:{segment.start_price:.2f}→{segment.end_price:.2f}")
    
    # 验证连续性
    is_continuous = verify_segment_continuity(result['segments'])
    
    if is_continuous:
        print("\n🎉 线段连续性验证通过！")
        print("✅ 修复成功：线段在图表中不再断裂")
    else:
        print("\n❌ 线段连续性验证失败")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)