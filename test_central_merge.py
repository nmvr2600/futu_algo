#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中枢识别功能合并后的效果
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from util.chanlun import ChanlunProcessor


def create_test_data():
    """创建测试数据"""
    # 创建一个更复杂的测试K线数据，能够形成中枢
    data = {
        'time_key': [
            '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
            '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
            '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
            '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20',
            '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-01-25'
        ],
        'open': [10, 11, 12, 11, 10, 9, 8, 9, 10, 11, 12, 13, 12, 11, 10, 11, 12, 13, 12, 11, 10, 11, 12, 13, 12],
        'high': [12, 13, 14, 12, 11, 10, 9, 11, 12, 13, 14, 15, 13, 12, 11, 13, 14, 15, 13, 12, 11, 13, 14, 15, 13],
        'low': [9, 10, 11, 9, 8, 7, 6, 8, 9, 10, 11, 12, 10, 9, 8, 10, 11, 12, 10, 9, 8, 10, 11, 12, 10],
        'close': [11, 12, 13, 10, 9, 8, 7, 10, 11, 12, 13, 14, 11, 10, 9, 12, 13, 14, 11, 10, 9, 12, 13, 14, 11],
        'volume': [1000, 1100, 1200, 900, 800, 700, 600, 900, 1000, 1100, 1200, 1300, 1000, 900, 800, 1100, 1200, 1300, 1000, 900, 800, 1100, 1200, 1300, 1000]
    }
    return pd.DataFrame(data)


def test_central_identification():
    """测试中枢识别功能"""
    print("开始测试中枢识别功能...")
    
    # 创建测试数据
    df = create_test_data()
    print(f"测试数据长度: {len(df)}")
    
    # 创建缠论处理器
    processor = ChanlunProcessor()
    
    # 处理数据
    result = processor.process(df)
    
    # 输出结果
    print(f"\n处理结果:")
    print(f"- 合并后K线数量: {len(result['merged_df'])}")
    print(f"- 分型数量: {len(result['fractals'])}")
    print(f"- 笔数量: {len(result['strokes'])}")
    print(f"- 中枢数量: {len(result['centrals'])}")
    
    # 输出中枢详细信息
    for i, central in enumerate(result['centrals']):
        print(f"  中枢 {i+1}: 高={central.high:.2f}, 低={central.low:.2f}, 索引={central.start_index}-{central.end_index}")
    
    print("\n测试完成.")


def main():
    test_central_identification()


if __name__ == "__main__":
    main()