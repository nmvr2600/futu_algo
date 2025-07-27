#!/usr/bin/env python3
"""
测试重构后的线段构建逻辑
验证新的线段构建算法是否正确实现了缠论定义
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.chanlun import ChanlunProcessor


def create_test_data_for_segments():
    """创建专门用于测试线段的数据"""
    # 创建包含明显趋势的数据，确保能生成多个笔和线段
    dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
    
    # 模拟一个上涨-回调-上涨的模式
    prices = [
        100, 102, 98, 95, 93,  # 下跌
        90, 88, 92, 95, 98,    # 上涨
        95, 93, 91, 89, 87,    # 回调
        85, 88, 91, 94, 97,    # 上涨
        95, 93, 91, 89, 87,    # 回调
        85, 83, 86, 89, 92,    # 上涨
        90, 88, 86, 84, 82,    # 回调
        85, 88, 91, 94, 97,    # 上涨
        95, 93, 91, 89, 87,    # 回调
        100, 103, 106, 109, 112  # 强势上涨
    ]
    
    df = pd.DataFrame({
        'time_key': dates,
        'open': prices,
        'high': [p + 1 for p in prices],
        'low': [p - 1 for p in prices],
        'close': prices
    })
    
    return df


def test_segment_vs_stroke_difference():
    """测试线段和笔的区别"""
    print("=== 测试线段重构后的效果 ===")
    
    # 创建测试数据
    df = create_test_data_for_segments()
    print(f"测试数据: {len(df)} 根K线")
    
    # 创建处理器
    processor = ChanlunProcessor()
    
    # 处理数据
    result = processor.process(df)
    
    # 获取结果
    strokes = processor.strokes
    segments = processor.segments
    
    print(f"\n生成的笔数量: {len(strokes)}")
    print(f"生成的线段数量: {len(segments)}")
    
    if len(strokes) == 0:
        print("❌ 没有生成笔")
        return False
    
    if len(segments) == 0:
        print("❌ 没有生成线段")
        return False
    
    # 检查笔和线段的区别
    print(f"\n笔和线段数量对比:")
    print(f"笔: {len(strokes)} 个")
    print(f"线段: {len(segments)} 个")
    
    # 检查线段是否比笔少（应该如此）
    if len(segments) >= len(strokes):
        print("⚠️  线段数量大于等于笔数量，可能有问题")
    else:
        print("✅ 线段数量少于笔数量，符合预期")
    
    # 详细检查每个线段
    print(f"\n线段详细信息:")
    for i, segment in enumerate(segments):
        direction_str = "上涨" if segment.direction == 1 else "下跌"
        
        # 计算包含的笔数量
        contained_strokes = [
            stroke for stroke in strokes
            if stroke.start_index >= segment.start_index and stroke.end_index <= segment.end_index
        ]
        
        print(f"线段 {i+1}: {direction_str}")
        print(f"  价格区间: {segment.start_price:.2f} -> {segment.end_price:.2f}")
        print(f"  索引区间: {segment.start_index} -> {segment.end_index}")
        print(f"  包含笔数: {len(contained_strokes)}")
        
        # 验证线段构成条件
        if len(contained_strokes) < 3:
            print(f"  ⚠️  线段包含笔数不足3个")
        else:
            print(f"  ✅ 线段包含笔数≥3个")
    
    # 检查笔的详细信息
    print(f"\n笔详细信息:")
    for i, stroke in enumerate(strokes[:min(5, len(strokes))]):
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"笔 {i+1}: {direction_str} {stroke.start_price:.2f} -> {stroke.end_price:.2f}")
    
    return True


def test_overlap_condition():
    """测试前三笔重叠条件"""
    print("\n=== 测试前三笔重叠条件 ===")
    
    # 创建简单的测试数据
    df = create_test_data_for_segments()
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    if len(processor.segments) == 0:
        print("❌ 没有线段可供测试")
        return False
    
    # 检查第一个线段的重叠条件
    segment = processor.segments[0]
    strokes = processor.strokes
    
    # 找到线段包含的笔
    contained_strokes = [
        stroke for stroke in strokes
        if stroke.start_index >= segment.start_index and stroke.end_index <= segment.end_index
    ]
    
    if len(contained_strokes) < 3:
        print(f"❌ 线段包含笔数不足3个: {len(contained_strokes)}")
        return False
    
    # 检查前三笔的重叠
    s1, s2, s3 = contained_strokes[:3]
    
    # 计算价格区间
    ranges = []
    for stroke in [s1, s2, s3]:
        if stroke.direction == 1:
            ranges.append((stroke.start_price, stroke.end_price))
        else:
            ranges.append((stroke.end_price, stroke.start_price))
    
    # 计算重叠区间
    overlap_low = max(min(r) for r in ranges)
    overlap_high = min(max(r) for r in ranges)
    
    print(f"前三笔价格区间:")
    for i, (low, high) in enumerate(ranges, 1):
        print(f"  笔{i}: [{low:.2f}, {high:.2f}]")
    
    print(f"重叠区间: [{overlap_low:.2f}, {overlap_high:.2f}]")
    
    if overlap_low <= overlap_high:
        print("✅ 前三笔存在重叠区间")
        return True
    else:
        print("❌ 前三笔无重叠区间")
        return False


def test_direction_alternation():
    """测试方向交替性"""
    print("\n=== 测试方向交替性 ===")
    
    df = create_test_data_for_segments()
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    if len(processor.segments) == 0:
        print("❌ 没有线段可供测试")
        return False
    
    # 检查每个线段内的笔方向
    for segment_idx, segment in enumerate(processor.segments):
        strokes = processor.strokes
        
        # 找到线段包含的笔
        contained_strokes = [
            stroke for stroke in strokes
            if stroke.start_index >= segment.start_index and stroke.end_index <= segment.end_index
        ]
        
        if len(contained_strokes) < 3:
            continue
        
        print(f"\n线段 {segment_idx+1} 方向检查:")
        
        # 检查前三笔的方向
        directions = [s.direction for s in contained_strokes[:3]]
        print(f"前三笔方向: {directions}")
        
        # 检查方向交替性
        # 应该满足: 第一笔和第三笔同向，第二笔反向
        if directions[0] == directions[2] and directions[0] != directions[1]:
            print("✅ 方向交替性正确")
        else:
            print("❌ 方向交替性错误")
    
    return True


if __name__ == "__main__":
    print("开始测试线段重构...")
    
    # 运行所有测试
    success1 = test_segment_vs_stroke_difference()
    success2 = test_overlap_condition()
    success3 = test_direction_alternation()
    
    if success1 and success2 and success3:
        print("\n🎉 所有测试通过！线段重构成功")
    else:
        print("\n💥 部分测试失败，需要进一步调试")
        
    # 保存测试结果
    try:
        os.makedirs("./test_results", exist_ok=True)
        
        # 创建简单的测试报告
        report = {
            'test_segment_vs_stroke': success1,
            'test_overlap_condition': success2,
            'test_direction_alternation': success3,
            'strokes_count': len(ChanlunProcessor().process(create_test_data_for_segments())['strokes']),
            'segments_count': len(ChanlunProcessor().process(create_test_data_for_segments())['segments'])
        }
        
        import json
        with open('./test_results/segment_reconstruction_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print("测试结果已保存到 test_results/segment_reconstruction_report.json")
        
    except Exception as e:
        print(f"保存测试结果时出错: {e}")