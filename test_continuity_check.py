#!/usr/bin/env python3
"""
线段连续性检查测试
验证修复后的线段构建算法是否解决了断点问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.chanlun import ChanlunProcessor
import pandas as pd

def create_test_data():
    """创建测试数据"""
    data = {
        'time_key': [
            '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
            '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10',
            '2024-01-11', '2024-01-12', '2024-01-13', '2024-01-14', '2024-01-15'
        ],
        'open': [100, 102, 101, 103, 105, 104, 102, 100, 98, 96, 94, 96, 98, 100, 102],
        'high': [105, 104, 103, 106, 107, 105, 103, 101, 99, 97, 95, 99, 101, 103, 105],
        'low': [95, 98, 99, 100, 102, 101, 99, 97, 95, 93, 91, 93, 95, 97, 99],
        'close': [103, 101, 102, 104, 106, 103, 101, 99, 97, 95, 93, 97, 99, 101, 103],
        'volume': [1000, 1200, 1100, 1300, 1400, 1250, 1150, 1050, 950, 850, 750, 900, 1000, 1100, 1200]
    }
    return pd.DataFrame(data)

def test_segment_continuity():
    """测试线段连续性"""
    print("🧪 开始线段连续性测试...")
    
    # 创建测试数据
    df = create_test_data()
    
    # 处理数据
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    segments = result['segments']
    
    print(f"📊 测试数据: {len(df)} 根K线")
    print(f"🔢 生成了 {len(segments)} 个线段")
    
    if len(segments) == 0:
        print("❌ 没有生成线段")
        return False
    
    if len(segments) == 1:
        print("✅ 只有一个线段，自然连续")
        return True
    
    # 检查连续性
    print("🔍 检查线段连续性:")
    all_continuous = True
    
    for i in range(1, len(segments)):
        prev_end = segments[i-1].end_index
        curr_start = segments[i].start_index
        
        if prev_end != curr_start:
            print(f"❌ 线段 {i-1} 结束 {prev_end} != 线段 {i} 开始 {curr_start}")
            all_continuous = False
        else:
            print(f"✅ 线段 {i-1} 和 {i} 连续: {prev_end}")
    
    # 检查覆盖完整性
    if segments:
        first_segment_start = segments[0].start_index
        last_segment_end = segments[-1].end_index
        
        print(f"📈 线段覆盖范围: {first_segment_start} -> {last_segment_end}")
        print(f"📊 数据总范围: 0 -> {len(df)-1}")
        
        if first_segment_start == 0 and last_segment_end == len(df)-1:
            print("✅ 线段完全覆盖数据")
        else:
            print("⚠️  线段未完全覆盖数据")
    
    return all_continuous

if __name__ == "__main__":
    success = test_segment_continuity()
    if success:
        print("\n🎉 线段连续性测试通过！")
    else:
        print("\n💥 线段连续性测试失败！")
    sys.exit(0 if success else 1)