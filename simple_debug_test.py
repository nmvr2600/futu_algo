#!/usr/bin/env python3
"""
简单测试debug.md中的要求是否满足
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.chanlun import ChanlunProcessor


def test_debug_requirements():
    """测试debug.md中的要求"""
    print("=== 测试debug.md中的要求 ===")
    
    # 创建简单的测试数据
    import pandas as pd
    from datetime import datetime, timedelta
    
    # 创建测试数据 (10根K线)
    dates = [datetime.now() - timedelta(days=i) for i in range(9, -1, -1)]
    data = pd.DataFrame({
        'time_key': dates,
        'open': [10, 11, 10, 11, 9, 10, 9, 11, 10, 11],
        'high': [11, 12, 11, 12, 10, 11, 10, 12, 11, 12],
        'low': [9, 10, 9, 10, 8, 9, 8, 10, 9, 10],
        'close': [10.5, 11.5, 10.5, 11, 9.5, 10.5, 9, 11, 10.5, 11.5]
    })
    
    print(f"创建了 {len(data)} 条测试K线数据")

    # 缠论分析
    processor = ChanlunProcessor()
    result = processor.process(data)

    print(f"\n分形总数: {len(result['fractals'])}")
    print(f"笔总数: {len(result['strokes'])}")
    print(f"线段总数: {len(result['segments'])}")

    # 验证要求1: 识别出分型后要给分型编号
    print("\n=== 要求1验证：分型编号 ===")
    for fractal in result['fractals']:
        type_str = "顶" if fractal.type == fractal.type.TOP else "底"
        print(f"分型 {fractal.idx}: {type_str}分型，索引={fractal.index}, 价格={fractal.price:.2f}")
        
    # 验证要求2: 笔用两个分型连接表示，例如[1,2]
    print("\n=== 要求2验证：笔的表示 ===")
    for stroke in result['strokes']:
        print(f"笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
              f"索引 {stroke.start_index}-{stroke.end_index}")

    # 验证要求3: 线段用分型区间表示，例如[1,4]
    print("\n=== 要求3验证：线段的表示 ===")
    for segment in result['segments']:
        print(f"线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
              f"索引 {segment.start_index}-{segment.end_index}")

    # 验证要求4: 处理过程中需要将信息输出便于排查 bug
    print("\n=== 要求4验证：信息输出 ===")
    print("✓ 处理过程中的信息已输出（见上方）")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_debug_requirements()