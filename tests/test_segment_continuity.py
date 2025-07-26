#!/usr/bin/env python3
"""
测试线段连续性
验证线段不会出现断掉的情况，确保线段之间正确连接
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from typing import List, Tuple

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, Stroke


@pytest.fixture
def simple_data():
    """创建简单测试数据"""
    test_data = []
    base_price = 100.0
    
    for i in range(20):
        if i < 5:  # 上涨段
            base_price += 2.0
        elif i < 10:  # 下跌段
            base_price -= 1.5
        elif i < 15:  # 上涨段
            base_price += 1.8
        else:  # 下跌段
            base_price -= 2.2
            
        test_data.append({
            'time_key': f'2024-01-{i+1:02d}',
            'open': base_price - 1.0,
            'high': base_price + 1.0,
            'low': base_price - 1.5,
            'close': base_price,
            'volume': 1000 + i * 100
        })
    
    return test_data

@pytest.fixture
def real_market_data():
    """创建真实市场测试数据"""
    test_data = []
    base_price = 100.0
    
    patterns = [
        {'days': 5, 'direction': 1, 'volatility': 2.0},
        {'days': 3, 'direction': -1, 'volatility': 1.0},
        {'days': 4, 'direction': 1, 'volatility': 1.5},
        {'days': 6, 'direction': -1, 'volatility': 2.5},
        {'days': 3, 'direction': 1, 'volatility': 1.2},
        {'days': 4, 'direction': -1, 'volatility': 1.8}
    ]
    
    current_day = 1
    for pattern in patterns:
        for day in range(pattern['days']):
            price_change = pattern['direction'] * pattern['volatility']
            base_price += price_change
            
            test_data.append({
                'time_key': f'2024-01-{current_day:02d}',
                'open': base_price - 0.5,
                'high': base_price + 1.0,
                'low': base_price - 1.0,
                'close': base_price,
                'volume': 1000 + current_day * 50
            })
            current_day += 1
    
    return test_data

def test_segment_continuity_with_simple_data(simple_data):
    """测试简单数据下的线段连续性"""
    print("测试简单数据下的线段连续性...")
    
    processor = ChanlunProcessor()
    df = pd.DataFrame(simple_data)
    result = processor.process(df)
    
    segments = result['segments']
    print(f"生成的线段数量: {len(segments)}")
    
    if len(segments) >= 2:
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            
            print(f"线段 {i-1}: 结束索引={prev_segment.end_index}, 分形={prev_segment.fractal_end}")
            print(f"线段 {i}: 开始索引={curr_segment.start_index}, 分形={curr_segment.fractal_start}")
            
            gap = curr_segment.start_index - prev_segment.end_index
            print(f"索引间隙: {gap}")
            
            assert gap <= 2, f"线段之间存在断层: 间隙={gap}"
    
    assert len(segments) >= 1, f"期望至少1个线段，实际生成{len(segments)}个"
    print(f"✓ 简单模式线段连续性测试通过，生成了{len(segments)}个线段")

def test_segment_continuity_with_real_market_pattern(real_market_data):
    """测试真实市场模式下的线段连续性"""
    print("测试真实市场模式下的线段连续性...")
    
    processor = ChanlunProcessor()
    df = pd.DataFrame(real_market_data)
    result = processor.process(df)
    
    segments = result['segments']
    print(f"生成的线段数量: {len(segments)}")
    
    for i, segment in enumerate(segments):
        print(f"线段 {i+1}: 方向={segment.direction}, "
              f"分形范围=[{segment.fractal_start},{segment.fractal_end}], "
              f"索引范围=[{segment.start_index},{segment.end_index}]")
    
    continuity_issues = []
    if len(segments) >= 2:
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            
            fractal_gap = curr_segment.fractal_start - prev_segment.fractal_end
            index_gap = curr_segment.start_index - prev_segment.end_index
            
            if fractal_gap > 1:
                continuity_issues.append({
                    'type': '分形断层',
                    'prev_fractal': prev_segment.fractal_end,
                    'curr_fractal': curr_segment.fractal_start,
                    'gap': fractal_gap
                })
            
            if index_gap > 1:
                continuity_issues.append({
                    'type': '索引断层',
                    'prev_index': prev_segment.end_index,
                    'curr_index': curr_segment.start_index,
                    'gap': index_gap
                })
    
    if continuity_issues:
        print("发现连续性问题的线段:")
        for issue in continuity_issues:
            print(f"  {issue}")
        assert False, "发现线段连续性问题"
    
    assert len(segments) > 0, f"期望至少1个线段，实际生成{len(segments)}个"
    print(f"✓ 真实市场模式线段连续性测试通过，生成了{len(segments)}个线段")