#!/usr/bin/env python3
"""
完整测试缠论处理流程中的笔连续性验证
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, FractalType


def create_test_data():
    """创建测试数据，确保能生成明显的分型"""
    # 创建能形成明显顶底分型的测试K线数据
    dates = pd.date_range('2024-01-01', periods=15, freq='D')
    data = {
        'time_key': dates,
        'open': [100, 102, 105, 103, 101, 104, 108, 106, 102, 107, 110, 108, 105, 109, 112],
        'high': [102, 105, 106, 104, 103, 108, 109, 107, 105, 110, 112, 110, 107, 112, 113],
        'low': [99, 101, 103, 101, 99, 102, 106, 104, 100, 105, 108, 106, 103, 107, 110],
        'close': [101, 103, 104, 102, 102, 106, 107, 105, 103, 108, 110, 107, 105, 110, 112],
        'volume': [1000] * 15
    }
    return pd.DataFrame(data)


def test_full_process():
    """测试完整的缠论处理流程"""
    print("=== 测试完整的缠论处理流程 ===")
    
    # 创建测试数据
    df = create_test_data()
    print(f"创建测试数据，共 {len(df)} 条K线记录")
    
    # 输出K线数据用于调试
    print("\nK线数据:")
    for i, row in df.iterrows():
        print(f"  {i}: open={row['open']:.2f}, high={row['high']:.2f}, low={row['low']:.2f}, close={row['close']:.2f}")
    
    # 创建处理器
    processor = ChanlunProcessor()
    
    # 处理数据
    result = processor.process(df)
    
    # 输出结果
    print(f"\n处理结果:")
    print(f"  合并后K线数量: {len(result['merged_df'])}")
    print(f"  分型数量: {len(result['fractals'])}")
    print(f"  笔数量: {len(result['strokes'])}")
    print(f"  线段数量: {len(result['segments'])}")
    print(f"  中枢数量: {len(result['centrals'])}")
    
    # 输出分型信息
    print(f"\n分型信息:")
    for fractal in result['fractals']:
        type_str = "顶" if fractal.type == FractalType.TOP else "底"
        print(f"  分型 {fractal.idx}: {type_str}分型，索引={fractal.index}, 价格={fractal.price:.2f}")
    
    # 输出笔信息
    print(f"\n笔信息:")
    for stroke in result['strokes']:
        direction_str = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
              f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
              f"索引 {stroke.start_index}->{stroke.end_index}")


def main():
    """主测试函数"""
    test_full_process()


if __name__ == "__main__":
    main()