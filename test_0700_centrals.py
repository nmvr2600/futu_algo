#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试0700.HK股票的中枢识别和合并功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from util.chanlun import ChanlunProcessor
from custom.chanlun_selector_demo import get_stock_data


def check_overlap(central1, central2):
    """检查两个中枢是否有重叠"""
    return max(central1.low, central2.low) <= min(central1.high, central2.high)


def test_0700_centrals():
    """测试0700.HK的中枢识别功能"""
    print("开始测试0700.HK的中枢识别功能...")
    
    # 获取0700.HK的数据
    data = get_stock_data("0700.HK", period="1y", interval="1d")
    print(f"获取到的数据长度: {len(data)}")
    
    if data.empty:
        print("无法获取0700.HK的数据")
        return
    
    # 创建缠论处理器
    processor = ChanlunProcessor()
    
    # 处理数据
    result = processor.process(data)
    
    # 输出结果
    print(f"\n处理结果:")
    print(f"- 合并后K线数量: {len(result['merged_df'])}")
    print(f"- 分型数量: {len(result['fractals'])}")
    print(f"- 笔数量: {len(result['strokes'])}")
    print(f"- 线段数量: {len(result['segments'])}")
    print(f"- 中枢数量: {len(result['centrals'])}")
    
    # 输出中枢详细信息
    for i, central in enumerate(result['centrals']):
        print(f"  中枢 {i+1}: 高={central.high:.2f}, 低={central.low:.2f}, 索引={central.start_index}-{central.end_index}")
        
        # 输出构成该中枢的笔信息
        if central.strokes:
            print(f"    构成笔数: {len(central.strokes)}")
            # 只显示前几笔和后几笔
            if len(central.strokes) <= 10:
                for j, stroke in enumerate(central.strokes):
                    print(f"      笔 {j+1}: 方向={'上涨' if stroke.direction == 1 else '下跌'}, 价格={stroke.start_price:.2f}->{stroke.end_price:.2f}")
            else:
                # 显示前3笔和后3笔
                for j in range(3):
                    stroke = central.strokes[j]
                    print(f"      笔 {j+1}: 方向={'上涨' if stroke.direction == 1 else '下跌'}, 价格={stroke.start_price:.2f}->{stroke.end_price:.2f}")
                print(f"      ... (省略 {len(central.strokes) - 6} 笔) ...")
                for j in range(len(central.strokes) - 3, len(central.strokes)):
                    stroke = central.strokes[j]
                    print(f"      笔 {j+1}: 方向={'上涨' if stroke.direction == 1 else '下跌'}, 价格={stroke.start_price:.2f}->{stroke.end_price:.2f}")
    
    # 检查中枢之间是否有重叠
    print("\n中枢重叠检查:")
    centrals = result['centrals']
    overlap_count = 0
    for i in range(len(centrals)):
        for j in range(i+1, len(centrals)):
            if check_overlap(centrals[i], centrals[j]):
                print(f"  中枢 {i+1} 和中枢 {j+1} 有重叠: [{centrals[i].low:.2f}-{centrals[i].high:.2f}] 与 [{centrals[j].low:.2f}-{centrals[j].high:.2f}]")
                overlap_count += 1
    
    if overlap_count == 0:
        print("  没有发现重叠的中枢")
    
    print("\n测试完成.")


def main():
    test_0700_centrals()


if __name__ == "__main__":
    main()