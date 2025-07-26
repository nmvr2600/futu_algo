#!/usr/bin/env python3
"""
调试分型识别逻辑的测试脚本
"""
import pandas as pd
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, FractalType


def debug_fractal_identification():
    """调试分型识别逻辑"""
    print("=== 调试分型识别逻辑 ===")

    # 构造测试数据 (已合并)
    # K1: 底分型, K3: 顶分型
    data = {
        "time_key": pd.to_datetime(
            ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
        ),
        "high": [11, 10, 11, 13, 12],
        "low": [9, 8, 9, 11, 11],
    }
    df = pd.DataFrame(data)

    print("测试数据:")
    for i in range(len(df)):
        print(f"  K{i}: high={df['high'].iloc[i]}, low={df['low'].iloc[i]}")

    # 执行处理
    processor = ChanlunProcessor()
    processor.merged_df = df  # 假设K线已合并
    result_fractals = processor.identify_fractals()

    print(f"\n识别到的分型 ({len(result_fractals)} 个):")
    for fractal in result_fractals:
        type_str = "顶" if fractal.type == FractalType.TOP else "底"
        print(
            f"  分型 {fractal.idx}: {type_str}分型，索引={fractal.index}, 价格={fractal.price}"
        )

    return result_fractals


if __name__ == "__main__":
    debug_fractal_identification()
