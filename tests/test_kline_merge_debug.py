#!/usr/bin/env python3
"""
调试K线合并逻辑的测试脚本
"""
import pandas as pd
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def debug_kline_merge():
    """调试K线合并逻辑"""
    print("=== 调试K线合并逻辑 ===")

    # 构造测试数据:
    # K0: 基础K线 (阳)
    # K1: 被K0向上包含
    # K2: 独立K线 (阴)
    # K3: 被K2向下包含
    # K4: 被合并后的K2_3向下包含
    data = {
        "time_key": pd.to_datetime(
            ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
        ),
        "open": [10.0, 10.8, 12.0, 11.5, 10.5],
        "high": [12.0, 11.5, 13.0, 12.0, 11.0],
        "low": [9.0, 10.5, 10.0, 11.0, 10.0],
        "close": [11.0, 11.2, 11.0, 11.2, 10.8],
    }
    df = pd.DataFrame(data)

    print("原始数据:")
    for i in range(len(df)):
        print(
            f"  K{i}: open={df['open'].iloc[i]}, high={df['high'].iloc[i]}, low={df['low'].iloc[i]}, close={df['close'].iloc[i]}"
        )

    # 执行处理
    processor = ChanlunProcessor()
    processor._merge_k_lines(df)

    print(
        f"\n合并后数据 ({len(processor.merged_df) if processor.merged_df is not None else 0} 根):"
    )
    if processor.merged_df is not None:
        for i in range(len(processor.merged_df)):
            row = processor.merged_df.iloc[i]
            print(
                f"  K{i}: open={row['open']}, high={row['high']}, low={row['low']}, close={row['close']}, original_indices={row['original_indices']}"
            )

    return processor


if __name__ == "__main__":
    debug_kline_merge()
