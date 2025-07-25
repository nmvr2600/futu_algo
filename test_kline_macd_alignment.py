#!/usr/bin/env python3
"""
测试K线与MACD对齐修复
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chanlun_advanced_visualizer import AdvancedChanlunVisualizer
from util.chanlun import ChanlunProcessor


def create_test_data():
    """创建测试数据"""
    # 创建一个简单的上升趋势数据
    days = 20
    base_data = {
        "time_key": pd.date_range("2024-01-01", periods=days, freq="D"),
        "open": [],
        "high": [],
        "low": [],
        "close": [],
    }

    # 创建上升趋势数据
    for i in range(days):
        base_price = 100 + i * 0.5
        noise = np.random.normal(0, 0.5)

        base_data["open"].append(base_price + noise)
        base_data["high"].append(base_price + 2 + abs(noise))
        base_data["low"].append(base_price - 2 - abs(noise))
        base_data["close"].append(base_price + noise * 0.5)

    return pd.DataFrame(base_data)


def test_kline_macd_alignment():
    """测试K线与MACD对齐"""
    print("=== 测试K线与MACD对齐 ===")

    # 创建测试数据
    df = create_test_data()
    print(f"测试数据长度: {len(df)}")

    # 创建处理器和可视化器
    processor = ChanlunProcessor()
    visualizer = AdvancedChanlunVisualizer()

    # 处理数据
    result = processor.process(df)
    if result is None:
        print("❌ 缠论分析失败")
        return False

    # 计算MACD
    macd_result = visualizer._calculate_macd(df)

    # 识别背驰
    divergences = visualizer._identify_divergences(df, result, macd_result)

    # 创建图表
    fig = visualizer.create_comprehensive_chart(df, result, "TEST")

    # 检查K线和MACD的数据点数量
    kline_count = len(df)
    macd_count = len(macd_result["macd_line"])

    print(f"K线数据点数量: {kline_count}")
    print(f"MACD数据点数量: {macd_count}")

    # 检查是否对齐
    if kline_count == macd_count:
        print("✅ K线与MACD数据点数量一致")
        alignment_status = True
    else:
        print("❌ K线与MACD数据点数量不一致")
        alignment_status = False

    # 检查背驰标记索引是否在有效范围内
    valid_divergences = 0
    invalid_divergences = 0
    for div in divergences:
        idx = div["price_index"]
        if idx < len(df) and idx < len(macd_result["macd_line"]):
            valid_divergences += 1
        else:
            invalid_divergences += 1
            print(f"❌ 背驰标记索引超出范围: {idx} (数据长度: {len(df)})")

    print(f"有效背驰标记: {valid_divergences}")
    print(f"无效背驰标记: {invalid_divergences}")

    if invalid_divergences == 0:
        print("✅ 所有背驰标记索引都在有效范围内")
        divergence_status = True
    else:
        print("❌ 存在超出范围的背驰标记索引")
        divergence_status = False

    # 总体测试结果
    overall_status = alignment_status and divergence_status

    if overall_status:
        print("\n🎉 K线与MACD对齐测试通过！")
    else:
        print("\n⚠️  K线与MACD对齐测试失败！")

    return overall_status


def main():
    """主函数"""
    try:
        result = test_kline_macd_alignment()
        return result
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
