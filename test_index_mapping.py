#!/usr/bin/env python3
import sys
import os
import pandas as pd

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom.chanlun_selector_demo import get_stock_data
from util.chanlun import ChanlunProcessor
from chanlun_advanced_visualizer import AdvancedChanlunVisualizer


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

    # 创建可视化器
    visualizer = AdvancedChanlunVisualizer()

    # 测试索引映射
    index_map = visualizer._create_index_mapping(result.get("merged_df", data), data)
    print(f"索引映射数量: {len(index_map)}")

    # 查看前几个映射关系
    print("前10个索引映射关系:")
    count = 0
    for merged_idx, original_idx in index_map.items():
        print(f"  合并索引{merged_idx} -> 原始索引{original_idx}")
        count += 1
        if count >= 10:
            break

    # 测试分形索引映射
    if result["fractals"]:
        print("前5个分形索引映射:")
        for i, f in enumerate(result["fractals"][:5]):
            original_idx = index_map.get(f.index, f.index)
            print(f"  分形{i}: 合并索引{f.index} -> 原始索引{original_idx}")

    # 测试笔索引映射
    if result["strokes"]:
        print("前5笔索引映射:")
        for i, s in enumerate(result["strokes"][:5]):
            start_original = index_map.get(s.start_index, s.start_index)
            end_original = index_map.get(s.end_index, s.end_index)
            print(
                f"  笔{i}: 合并索引{[s.start_index, s.end_index]} -> 原始索引{[start_original, end_original]}"
            )


if __name__ == "__main__":
    main()
