#!/usr/bin/env python3
"""
验证索引映射正确性的测试脚本
"""
import pandas as pd
import sys
import os
import yfinance as yf

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, FractalType
from chanlun_advanced_visualizer import AdvancedChanlunVisualizer


def get_stock_data(symbol, period="1y", interval="1d"):
    """
    获取单个股票的数据并确保列名正确
    :param symbol: 股票代码
    :param period: 数据周期 ("1y", "2y", "5y", "10y", "ytd", "max")
    :param interval: 数据间隔 ("1d", "1wk", "1mo", "5m", "15m", "30m", "1h")
    """
    try:
        # 使用yfinance获取指定周期和间隔的数据
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)

        # 确保列名正确
        if not data.empty:
            # 重命名列以匹配缠论处理器的期望
            data = data.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )
            # 确保有time_key列
            data["time_key"] = pd.to_datetime(data.index).strftime("%Y-%m-%d %H:%M:%S")
        return data
    except Exception as e:
        print(f"获取{symbol}数据时出错: {e}")
        return pd.DataFrame()


def validate_index_mapping():
    """验证索引映射正确性"""
    print("=== 验证索引映射正确性 ===")

    # 获取0700.HK数据，使用50根K线
    stock_code = "0700.HK"
    print(f"正在获取 {stock_code} 的数据...")

    try:
        # 获取数据
        data = get_stock_data(stock_code, period="6mo", interval="1d")

        # 使用最近50根K线
        data = data.tail(50).reset_index(drop=True)
        print(f"使用最近 {len(data)} 根K线进行分析")

        if len(data) < 30:
            print(f"当前{len(data)}根K线，数据不足无法进行完整分析")
            return

        # 显示数据基本信息
        print(
            f"数据时间范围: {data['time_key'].iloc[0]} 到 {data['time_key'].iloc[-1]}"
        )
        print(f"价格范围: {data['low'].min():.2f} - {data['high'].max():.2f}")

        # 缠论分析
        print("\n开始缠论分析...")
        processor = ChanlunProcessor()
        result = processor.process(data)

        # 显示分析结果
        print(f"\n分析结果:")
        print(f"  合并后K线数量: {len(result['merged_df'])}")
        print(f"  分型数量: {len(result['fractals'])}")
        print(f"  笔数量: {len(result['strokes'])}")
        print(f"  线段数量: {len(result['segments'])}")
        print(f"  中枢数量: {len(result['centrals'])}")

        # 创建可视化器
        visualizer = AdvancedChanlunVisualizer()

        # 创建索引映射
        index_map = visualizer._create_index_map(data)
        merged_index_map = visualizer._create_merged_index_map(result)
        fractal_number_map = visualizer._create_fractal_number_map(result)

        print(f"\n索引映射详情:")
        print(f"  原始索引映射数量: {len(index_map)}")
        print(f"  合并索引映射数量: {len(merged_index_map)}")
        print(f"  分形编号映射数量: {len(fractal_number_map)}")

        # 验证索引映射的完整性
        print(f"\n验证索引映射完整性:")
        total_original_indices = sum(
            len(indices) for indices in result["index_mapping"].values()
        )
        print(f"  合并前K线总数: {len(data)}")
        print(f"  合并后K线总数: {len(result['merged_df'])}")
        print(f"  索引映射总数: {total_original_indices}")
        if total_original_indices == len(data):
            print("  ✅ 索引映射完整性验证通过")
        else:
            print("  ❌ 索引映射完整性验证失败")

        # 验证分型索引映射
        print(f"\n验证分型索引映射:")
        for i, fractal in enumerate(result["fractals"][:5]):  # 只检查前5个分型
            original_idx = fractal.index
            price = fractal.price
            type_str = "顶" if fractal.type.value == "top" else "底"
            number = fractal_number_map.get(original_idx, "?")

            # 应用合并索引映射
            if merged_index_map:
                mapped_idx = merged_index_map.get(original_idx, original_idx)
            else:
                mapped_idx = original_idx

            # 应用索引映射
            if index_map:
                final_idx = index_map.get(mapped_idx, mapped_idx)
            else:
                final_idx = mapped_idx

            print(f"  分型 {number} ({type_str}):")
            print(f"    原始索引={original_idx} (价格={price:.2f})")
            print(f"    合并映射={mapped_idx}")
            print(f"    最终索引={final_idx}")
            if isinstance(final_idx, int) and final_idx < len(data):
                actual_price = (
                    data["high"].iloc[final_idx]
                    if fractal.type.value == "top"
                    else data["low"].iloc[final_idx]
                )
                print(f"    实际K线价格={actual_price:.2f}")
                if abs(actual_price - price) <= 0.01:
                    print("    ✅ 价格匹配")
                else:
                    print(
                        f"    ❌ 价格不匹配: 计算价格={price:.2f}, 实际价格={actual_price:.2f}"
                    )
            else:
                print(f"    ❌ 索引超出范围: {final_idx} >= {len(data)}")

        # 验证笔索引映射
        print(f"\n验证笔索引映射:")
        for i, stroke in enumerate(result["strokes"][:3]):  # 只检查前3笔
            start_idx = stroke.start_index
            end_idx = stroke.end_index
            start_price = stroke.start_price
            end_price = stroke.end_price

            # 应用合并索引映射
            if merged_index_map:
                mapped_start_idx = merged_index_map.get(start_idx, start_idx)
                mapped_end_idx = merged_index_map.get(end_idx, end_idx)
            else:
                mapped_start_idx = start_idx
                mapped_end_idx = end_idx

            # 应用索引映射
            if index_map:
                final_start_idx = index_map.get(mapped_start_idx, mapped_start_idx)
                final_end_idx = index_map.get(mapped_end_idx, mapped_end_idx)
            else:
                final_start_idx = mapped_start_idx
                final_end_idx = mapped_end_idx

            print(f"  笔 {i+1}:")
            print(
                f"    起始索引: {start_idx} -> {mapped_start_idx} -> {final_start_idx}"
            )
            print(f"    结束索引: {end_idx} -> {mapped_end_idx} -> {final_end_idx}")
            if (
                isinstance(final_start_idx, int)
                and final_start_idx < len(data)
                and isinstance(final_end_idx, int)
                and final_end_idx < len(data)
            ):
                actual_start_price = (
                    data["high"].iloc[final_start_idx]
                    if stroke.direction == 1
                    else data["low"].iloc[final_start_idx]
                )
                actual_end_price = (
                    data["high"].iloc[final_end_idx]
                    if stroke.direction == -1
                    else data["low"].iloc[final_end_idx]
                )
                print(
                    f"    实际起始价格={actual_start_price:.2f}, 实际结束价格={actual_end_price:.2f}"
                )
                if (
                    abs(actual_start_price - start_price) <= 0.01
                    and abs(actual_end_price - end_price) <= 0.01
                ):
                    print("    ✅ 价格匹配")
                else:
                    print(
                        f"    ❌ 价格不匹配: 起始价格={start_price:.2f}->{actual_start_price:.2f}, 结束价格={end_price:.2f}->{actual_end_price:.2f}"
                    )
            else:
                print(f"    ❌ 索引超出范围")

        # 验证线段索引映射
        print(f"\n验证线段索引映射:")
        for i, segment in enumerate(result["segments"][:3]):  # 只检查前3线段
            start_idx = segment.start_index
            end_idx = segment.end_index
            start_price = segment.start_price
            end_price = segment.end_price

            # 应用合并索引映射
            if merged_index_map:
                mapped_start_idx = merged_index_map.get(start_idx, start_idx)
                mapped_end_idx = merged_index_map.get(end_idx, end_idx)
            else:
                mapped_start_idx = start_idx
                mapped_end_idx = end_idx

            # 应用索引映射
            if index_map:
                final_start_idx = index_map.get(mapped_start_idx, mapped_start_idx)
                final_end_idx = index_map.get(mapped_end_idx, mapped_end_idx)
            else:
                final_start_idx = mapped_start_idx
                final_end_idx = mapped_end_idx

            print(f"  线段 {i+1}:")
            print(
                f"    起始索引: {start_idx} -> {mapped_start_idx} -> {final_start_idx}"
            )
            print(f"    结束索引: {end_idx} -> {mapped_end_idx} -> {final_end_idx}")
            if (
                isinstance(final_start_idx, int)
                and final_start_idx < len(data)
                and isinstance(final_end_idx, int)
                and final_end_idx < len(data)
            ):
                actual_start_price = (
                    data["high"].iloc[final_start_idx]
                    if segment.direction == 1
                    else data["low"].iloc[final_start_idx]
                )
                actual_end_price = (
                    data["high"].iloc[final_end_idx]
                    if segment.direction == -1
                    else data["low"].iloc[final_end_idx]
                )
                print(
                    f"    实际起始价格={actual_start_price:.2f}, 实际结束价格={actual_end_price:.2f}"
                )
                if (
                    abs(actual_start_price - start_price) <= 0.01
                    and abs(actual_end_price - end_price) <= 0.01
                ):
                    print("    ✅ 价格匹配")
                else:
                    print(
                        f"    ❌ 价格不匹配: 起始价格={start_price:.2f}->{actual_start_price:.2f}, 结束价格={end_price:.2f}->{actual_end_price:.2f}"
                    )
            else:
                print(f"    ❌ 索引超出范围")

        # 验证中枢索引映射
        print(f"\n验证中枢索引映射:")
        for i, central in enumerate(result["centrals"][:2]):  # 只检查前2个中枢
            start_idx = central.start_index
            end_idx = central.end_index
            high_price = central.high
            low_price = central.low

            # 应用合并索引映射
            if merged_index_map:
                mapped_start_idx = merged_index_map.get(start_idx, start_idx)
                mapped_end_idx = merged_index_map.get(end_idx, end_idx)
            else:
                mapped_start_idx = start_idx
                mapped_end_idx = end_idx

            # 应用索引映射
            if index_map:
                final_start_idx = index_map.get(mapped_start_idx, mapped_start_idx)
                final_end_idx = index_map.get(mapped_end_idx, mapped_end_idx)
            else:
                final_start_idx = mapped_start_idx
                final_end_idx = mapped_end_idx

            print(f"  中枢 {i+1}:")
            print(
                f"    起始索引: {start_idx} -> {mapped_start_idx} -> {final_start_idx}"
            )
            print(f"    结束索引: {end_idx} -> {mapped_end_idx} -> {final_end_idx}")
            if (
                isinstance(final_start_idx, int)
                and final_start_idx < len(data)
                and isinstance(final_end_idx, int)
                and final_end_idx < len(data)
            ):
                actual_high_price = data["high"].iloc[final_start_idx]
                actual_low_price = data["low"].iloc[final_end_idx]
                print(
                    f"    实际高点价格={actual_high_price:.2f}, 实际低点价格={actual_low_price:.2f}"
                )
                # 中枢验证相对宽松，只要在合理范围内即可
                if high_price >= actual_low_price and low_price <= actual_high_price:
                    print("    ✅ 价格范围合理")
                else:
                    print(
                        f"    ❌ 价格范围不合理: 高点={high_price:.2f}>={actual_low_price:.2f}, 低点={low_price:.2f}<={actual_high_price:.2f}"
                    )
            else:
                print(f"    ❌ 索引超出范围")

        return True

    except Exception as e:
        print(f"验证过程中出错: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    validate_index_mapping()
