#!/usr/bin/env python3
import sys
import os
import pandas as pd

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom.chanlun_selector_demo import get_stock_data
from util.chanlun import ChanlunProcessor


def main():
    # 获取真实数据
    data = get_stock_data("0700.HK", period="2y", interval="1d")
    print(f"原始数据长度: {len(data)}")

    # 处理缠论
    processor = ChanlunProcessor()
    result = processor.process(data)
    print(f'合并后数据长度: {len(result["merged_df"])}')
    print(f'分形数量: {len(result["fractals"])}')
    print(f'笔数量: {len(result["strokes"])}')
    print(f'中枢数量: {len(result["centrals"])}')

    # 查看前几个分形的索引
    if result["fractals"]:
        print("前5个分形索引:")
        for i, f in enumerate(result["fractals"][:5]):
            print(f"  {i}: {f.index}")

    # 查看前几笔的索引
    if result["strokes"]:
        print("前5笔索引:")
        for i, s in enumerate(result["strokes"][:5]):
            print(f"  {i}: start={s.start_index}, end={s.end_index}")

    # 查看合并数据中的original_indices
    if len(result["merged_df"]) > 0:
        print("合并数据中的original_indices示例:")
        for i in range(min(5, len(result["merged_df"]))):
            indices = result["merged_df"].iloc[i]["original_indices"]
            print(f"  合并K线{i}: {indices}")


if __name__ == "__main__":
    main()
