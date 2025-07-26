#!/usr/bin/env python3
"""
详细调试位置映射问题的测试脚本
"""
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor, FractalType
from custom.chanlun_selector_demo import get_stock_data
from chanlun_advanced_visualizer import AdvancedChanlunVisualizer


def debug_detailed_position_mapping():
    """详细调试位置映射问题"""
    print("=== 详细调试位置映射问题 ===")

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

        # 详细检查前几个分型的位置映射
        print(f"\n前5个分型位置映射详情:")
        for i, fractal in enumerate(result["fractals"][:5]):
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

        # 详细检查前几笔的位置映射
        print(f"\n前3笔位置映射详情:")
        for i, stroke in enumerate(result["strokes"][:3]):
            start_idx = stroke.start_index
            end_idx = stroke.end_index
            start_price = stroke.start_price
            end_price = stroke.end_price
            direction_str = "上涨" if stroke.direction == 1 else "下跌"

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

            print(f"  笔 {i+1} ({direction_str}):")
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

        # 详细检查前几个线段的位置映射
        print(f"\n前2个线段位置映射详情:")
        for i, segment in enumerate(result["segments"][:2]):
            start_idx = segment.start_index
            end_idx = segment.end_index
            start_price = segment.start_price
            end_price = segment.end_price
            direction_str = "上涨" if segment.direction == 1 else "下跌"

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

            print(f"  线段 {i+1} ({direction_str}):")
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

        # 详细检查前几个中枢的位置映射
        print(f"\n前1个中枢位置映射详情:")
        for i, central in enumerate(result["centrals"][:1]):
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

        # 创建详细调试图表
        print(f"\n正在生成详细调试图表...")
        create_detailed_debug_chart(
            data, result, index_map, merged_index_map, fractal_number_map
        )

        return True

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback

        traceback.print_exc()
        return False


def create_detailed_debug_chart(
    data, result, index_map, merged_index_map, fractal_number_map
):
    """创建详细调试图表，显示位置映射"""
    fig, ax = plt.subplots(figsize=(20, 12))

    # 转换时间格式
    df = data.sort_values("time_key").reset_index(drop=True)
    dates = pd.to_datetime(df["time_key"])

    # 绘制K线
    for i, (date, row) in enumerate(zip(dates, df.itertuples())):
        open_price = row.open
        high_price = row.high
        low_price = row.low
        close_price = row.close

        color = "red" if close_price >= open_price else "green"

        # 绘制实体
        height = abs(close_price - open_price)
        bottom = min(open_price, close_price)
        rect = Rectangle(
            (i - 0.3, bottom),
            0.6,
            height,
            facecolor=color,
            alpha=0.8,
            edgecolor=color,
        )
        ax.add_patch(rect)

        # 绘制影线
        ax.plot([i, i], [low_price, high_price], color=color, linewidth=1)

    # 绘制分形标注
    fractals = result["fractals"]
    top_fractals = [f for f in fractals if f.type.value == "top"]
    bottom_fractals = [f for f in fractals if f.type.value == "bottom"]

    # 顶分型
    if top_fractals:
        top_indices = [f.index for f in top_fractals]
        top_prices = [f.price for f in top_fractals]
        top_numbers = (
            [fractal_number_map.get(f.index, "?") for f in top_fractals]
            if fractal_number_map
            else ["?" for _ in top_fractals]
        )

        # 应用合并索引映射
        if merged_index_map:
            top_indices = [merged_index_map.get(idx, idx) for idx in top_indices]

        # 应用索引映射
        if index_map:
            top_indices = [index_map.get(idx, idx) for idx in top_indices]

        ax.scatter(
            top_indices,
            top_prices,
            color="red",
            marker="v",
            s=120,
            label="顶分型",
            zorder=5,
            edgecolors="black",
        )

        # 添加价格标签和编号
        for idx, price, number in zip(top_indices, top_prices, top_numbers):
            # 价格标签
            ax.annotate(
                f"{price:.2f}",
                (idx, price),
                xytext=(0, 10),
                textcoords="offset points",
                fontsize=9,
                color="red",
                ha="center",
                va="bottom",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
            )

            # 编号标签
            ax.annotate(
                f"{number}",
                (idx, price),
                xytext=(0, 25),
                textcoords="offset points",
                fontsize=10,
                color="white",
                ha="center",
                va="bottom",
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="red",
                    alpha=0.9,
                    edgecolor="black",
                ),
            )

    # 底分型
    if bottom_fractals:
        bottom_indices = [f.index for f in bottom_fractals]
        bottom_prices = [f.price for f in bottom_fractals]
        bottom_numbers = (
            [fractal_number_map.get(f.index, "?") for f in bottom_fractals]
            if fractal_number_map
            else ["?" for _ in bottom_fractals]
        )

        # 应用合并索引映射
        if merged_index_map:
            bottom_indices = [merged_index_map.get(idx, idx) for idx in bottom_indices]

        # 应用索引映射
        if index_map:
            bottom_indices = [index_map.get(idx, idx) for idx in bottom_indices]

        ax.scatter(
            bottom_indices,
            bottom_prices,
            color="green",
            marker="^",
            s=120,
            label="底分型",
            zorder=5,
            edgecolors="black",
        )

        # 添加价格标签和编号
        for idx, price, number in zip(bottom_indices, bottom_prices, bottom_numbers):
            # 价格标签
            ax.annotate(
                f"{price:.2f}",
                (idx, price),
                xytext=(0, -15),
                textcoords="offset points",
                fontsize=9,
                color="green",
                ha="center",
                va="top",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
            )

            # 编号标签
            ax.annotate(
                f"{number}",
                (idx, price),
                xytext=(0, -30),
                textcoords="offset points",
                fontsize=10,
                color="white",
                ha="center",
                va="top",
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="green",
                    alpha=0.9,
                    edgecolor="black",
                ),
            )

    # 绘制笔
    strokes = result["strokes"]
    for i, stroke in enumerate(strokes[:5]):  # 只绘制前5笔
        start_idx = stroke.start_index
        end_idx = stroke.end_index
        start_price = stroke.start_price
        end_price = stroke.end_price

        # 应用合并索引映射
        if merged_index_map:
            start_idx = merged_index_map.get(start_idx, start_idx)
            end_idx = merged_index_map.get(end_idx, end_idx)

        # 应用索引映射
        if index_map:
            start_idx = index_map.get(start_idx, start_idx)
            end_idx = index_map.get(end_idx, end_idx)

        # 确保索引在有效范围内
        start_idx = max(0, min(start_idx, len(df) - 1))
        end_idx = max(0, min(end_idx, len(df) - 1))

        color = "blue" if stroke.direction == 1 else "orange"
        linewidth = 3 if i == len(strokes) - 1 else 2  # 最后一笔加粗

        # 即使在相同索引也绘制一个点，确保视觉连续性
        ax.plot(
            [start_idx, end_idx],
            [start_price, end_price],
            color=color,
            linewidth=linewidth,
            alpha=0.8,
            linestyle="--",  # 笔用虚线显示
            solid_capstyle="round",
            solid_joinstyle="round",
        )

        # 在折线连接处添加小圆点突出起点和终点
        ax.scatter(
            [start_idx, end_idx],
            [start_price, end_price],
            color=color,
            s=15,
            alpha=0.8,
            zorder=10,
        )

        # 添加笔的标签 - 在起始和结束点附近标注分形编号
        # 获取起始和结束分形的编号
        start_number = (
            fractal_number_map.get(stroke.start_index, "?")
            if fractal_number_map
            else "?"
        )
        end_number = (
            fractal_number_map.get(stroke.end_index, "?") if fractal_number_map else "?"
        )

        # 起始点标签 - 放在K线上方或下方，避免重叠
        if stroke.direction == 1:  # 上升笔
            ax.annotate(
                f"[{start_number},{end_number}]",
                (start_idx, start_price),
                xytext=(0, 15),
                textcoords="offset points",
                fontsize=9,
                color=color,
                fontweight="bold",
                ha="center",
                va="bottom",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="white",
                    alpha=0.8,
                    edgecolor=color,
                ),
            )
        else:  # 下降笔
            ax.annotate(
                f"[{start_number},{end_number}]",
                (start_idx, start_price),
                xytext=(0, -20),
                textcoords="offset points",
                fontsize=9,
                color=color,
                fontweight="bold",
                ha="center",
                va="top",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="white",
                    alpha=0.8,
                    edgecolor=color,
                ),
            )

    # 绘制线段
    segments = result["segments"]
    for i, segment in enumerate(segments[:3]):  # 只绘制前3线段
        # 获取线段的起始和结束索引及价格
        start_idx = segment.start_index
        end_idx = segment.end_index
        start_price = segment.start_price
        end_price = segment.end_price
        direction = segment.direction

        # 应用合并索引映射
        if merged_index_map:
            start_idx = merged_index_map.get(start_idx, start_idx)
            end_idx = merged_index_map.get(end_idx, end_idx)

        # 应用索引映射
        if index_map:
            start_idx = index_map.get(start_idx, start_idx)
            end_idx = index_map.get(end_idx, end_idx)

        # 确保索引在有效范围内
        start_idx = max(0, min(start_idx, len(df) - 1))
        end_idx = max(0, min(end_idx, len(df) - 1))

        # 根据方向选择颜色
        color = "purple" if direction == 1 else "cyan"

        # 绘制线段，线宽为3px，确保连续连接
        ax.plot(
            [start_idx, end_idx],
            [start_price, end_price],
            color=color,
            linewidth=4,
            alpha=0.8,
            linestyle="-",  # 线段用实线显示
            solid_capstyle="round",
            solid_joinstyle="round",
        )

        # 在折线连接处添加圆点，提高视觉清晰度
        ax.scatter(
            [start_idx, end_idx],
            [start_price, end_price],
            color=color,
            s=15,
            alpha=0.8,
            zorder=15,
        )

        # 添加线段的标签 - 使用 [起始分形编号,结束分形编号] 格式标注
        mid_idx = (start_idx + end_idx) / 2
        mid_price = (start_price + end_price) / 2

        # 获取起始和结束分形的编号
        start_number = (
            fractal_number_map.get(segment.start_index, "?")
            if fractal_number_map
            else "?"
        )
        end_number = (
            fractal_number_map.get(segment.end_index, "?")
            if fractal_number_map
            else "?"
        )

        # 使用 [起始分形编号,结束分形编号] 格式标注
        ax.annotate(
            f"[{start_number},{end_number}]",
            (mid_idx, mid_price),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=10,
            color=color,
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                alpha=0.9,
                edgecolor=color,
            ),
        )

    # 绘制中枢
    centrals = result["centrals"]
    for i, central in enumerate(centrals[:2]):  # 只绘制前2个中枢
        # 转换索引以匹配绘图位置
        start_idx = central.start_index
        end_idx = central.end_index

        # 应用合并索引映射
        if merged_index_map:
            start_idx = merged_index_map.get(start_idx, start_idx)
            end_idx = merged_index_map.get(end_idx, end_idx)

        # 应用索引映射
        if index_map:
            start_idx = index_map.get(start_idx, start_idx)
            end_idx = index_map.get(end_idx, end_idx)

        # 确保索引在有效范围内
        start_idx = max(0, min(start_idx, len(df) - 1))
        end_idx = max(0, min(end_idx, len(df) - 1))

        high_price = central.high
        low_price = central.low

        color = "magenta"

        # 绘制中枢矩形
        width = end_idx - start_idx
        height = high_price - low_price
        rect = Rectangle(
            (start_idx, low_price),
            width,
            height,
            facecolor="lavender",
            alpha=0.4,
            edgecolor=color,
            linewidth=2,
            linestyle="--",
        )
        ax.add_patch(rect)

        # 添加中枢详细信息
        mid_idx = start_idx + width / 2
        mid_price = (high_price + low_price) / 2

        info_text = f"中枢{i+1}\n{low_price:.2f}-{high_price:.2f}\n区间:{height:.2f}"

        ax.text(
            mid_idx,
            mid_price,
            info_text,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=color,
                alpha=0.7,
                edgecolor=color,
            ),
        )

    # 设置图表
    ax.set_title(
        f"0700.HK 位置映射调试图表\n红色向下箭头=顶分型，绿色向上箭头=底分型",
        fontsize=16,
        fontweight="bold",
    )
    ax.set_ylabel("价格", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))

    # 价格格式化
    ax.yaxis.set_major_formatter(lambda x, p: f"{x:.2f}")

    # 设置x轴日期格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # 调整布局
    plt.tight_layout()

    # 保存图表
    save_dir = "./debug_reports"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_path = os.path.join(save_dir, f"0700.HK_{timestamp}_position_debug.png")
    plt.savefig(chart_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"详细调试图表已保存到: {chart_path}")
    return chart_path


if __name__ == "__main__":
    debug_detailed_position_mapping()
