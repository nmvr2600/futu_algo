#!/usr/bin/env python3
"""
缠论高级可视化工具
生成包含K线图、分形、笔、中枢的详细可视化报告
支持HTML报告和交互式图表
"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages
import json

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from util.chanlun import ChanlunProcessor
from custom.chanlun_selector_demo import get_stock_data
from util.global_vars import *


class AdvancedChanlunVisualizer:
    """高级缠论可视化器"""

    def __init__(self, figsize=(20, 12)):
        self.figsize = figsize
        plt.rcParams["font.sans-serif"] = ["SimHei", "Arial Unicode MS", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

        # 颜色配置
        self.colors = {
            "up_stroke": "#1f77b4",
            "down_stroke": "#ff7f0e",
            "top_fractal": "#d62728",
            "bottom_fractal": "#2ca02c",
            "central": "#9467bd",
            "central_fill": "#e6e6fa",
            "bullish": "#26a69a",
            "bearish": "#ef5350",
        }

    def create_comprehensive_chart(self, df, result, stock_code, save_path=None):
        """创建缠论背驰分析图表"""
        fig = plt.figure(figsize=(20, 10))

        # 创建子图布局 - 主图和MACD副图
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)

        # 主K线图
        ax1 = fig.add_subplot(gs[0])
        # MACD副图
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        # 获取合并后的K线数据
        merged_df = result.get("merged_df", df)
        merged_df = merged_df.sort_values("time_key").reset_index(drop=True)
        # 使用原始df的dates
        dates = pd.to_datetime(df["time_key"])

        # 创建索引映射：原始索引 -> 合并后索引
        original_to_merged_map = {}
        if "original_indices" in merged_df.columns:
            for merged_idx, row in merged_df.iterrows():
                original_indices = row["original_indices"]
                for orig_idx in original_indices:
                    original_to_merged_map[orig_idx] = merged_idx

        # 计算MACD (必须使用原始数据 df)
        macd_result = self._calculate_macd(df)

        # 识别背驰 (使用原始df计算的MACD)
        divergences = self._identify_divergences(df, result, macd_result)

        # 绘制主图表
        self._plot_enhanced_kline(
            ax1, merged_df, dates, result, divergences, original_to_merged_map
        )
        self._plot_macd(ax2, df, macd_result, divergences)

        # 设置标题
        fig.suptitle(
            f"{stock_code} - 缠论背驰分析\n"
            f'分形:{len(result["fractals"])} | '
            f'笔:{len(result["strokes"])} | '
            f'中枢:{len(result["centrals"])} | '
            f"背驰:{len(divergences)}",
            fontsize=16,
            fontweight="bold",
            y=0.98,
        )

        # 调整布局
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
            print(f"背驰分析图表已保存到: {save_path}")

        return fig

    def _identify_divergences(self, df, result, macd_result):
        """识别背驰信号"""
        divergences = []

        # 获取笔数据
        strokes = result["strokes"]
        if len(strokes) < 2:
            return divergences

        # 获取MACD数据
        macd_line = macd_result["macd_line"]

        # 检查相邻笔之间的背驰
        for i in range(1, len(strokes)):
            current_stroke = strokes[i]
            prev_stroke = strokes[i - 1]

            # 验证笔的方向交替性
            if current_stroke.direction == prev_stroke.direction:
                continue  # 相邻笔方向相同，跳过

            # 价格新高/新低
            price_direction = 1 if current_stroke.direction == 1 else -1

            # 确保索引在有效范围内
            current_idx = min(current_stroke.end_index, len(macd_line) - 1)
            prev_idx = min(prev_stroke.end_index, len(macd_line) - 1)

            if current_idx < 0 or prev_idx < 0:
                continue

            current_macd = macd_line.iloc[current_idx]
            prev_macd = macd_line.iloc[prev_idx]

            # 背驰条件：价格创新高/低，但MACD没有相应创新高/低
            if price_direction == 1:  # 上涨
                if (
                    current_stroke.end_price > prev_stroke.end_price
                    and current_macd < prev_macd
                ):
                    divergences.append(
                        {
                            "type": "顶背驰",
                            "stroke_index": i,
                            "price_index": current_stroke.end_index,
                            "price": current_stroke.end_price,
                            "macd_value": current_macd,
                        }
                    )
            else:  # 下跌
                if (
                    current_stroke.end_price < prev_stroke.end_price
                    and current_macd > prev_macd
                ):
                    divergences.append(
                        {
                            "type": "底背驰",
                            "stroke_index": i,
                            "price_index": current_stroke.end_index,
                            "price": current_stroke.end_price,
                            "macd_value": current_macd,
                        }
                    )

        return divergences

    def _plot_enhanced_kline(self, ax, df, dates, result, divergences, index_map=None):
        """绘制增强版K线图，包含背驰标记"""
        # 使用合并后的数据绘制K线
        merged_df = result.get("merged_df", df)
        if merged_df is None or merged_df.empty:
            merged_df = df

        # 使用原始df进行K线绘制，保持数据一致性
        for i in range(len(df)):
            row = df.iloc[i]
            open_price = row.open
            high_price = row.high
            low_price = row.low
            close_price = row.close

            # 使用索引映射来确定绘图位置
            plot_index = i
            if index_map:
                plot_index = index_map.get(i, i)

            color = (
                self.colors["bullish"]
                if close_price >= open_price
                else self.colors["bearish"]
            )

            # 绘制实体
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            rect = Rectangle(
                (plot_index - 0.3, bottom),
                0.6,
                height,
                facecolor=color,
                alpha=0.8,
                edgecolor=color,
            )
            ax.add_patch(rect)

            # 绘制影线
            ax.plot(
                [plot_index, plot_index],
                [low_price, high_price],
                color=color,
                linewidth=1,
            )

        # 绘制分形
        self._plot_fractals_detailed(ax, df, result["fractals"], index_map)

        # 绘制笔
        self._plot_strokes_detailed(ax, df, result["strokes"], index_map)

        # 绘制中枢
        self._plot_centrals_detailed(ax, df, result["centrals"], index_map)

        # 标记背驰信号
        self._plot_divergences(ax, df, divergences, index_map)

        # 设置网格和标签
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_ylabel("价格", fontsize=12)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))

        # 价格格式化
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.2f}"))

    def _plot_fractals_detailed(self, ax, df, fractals, index_map=None):
        """详细绘制分形"""
        if not fractals:
            return

        top_fractals = [f for f in fractals if f.type.value == "top"]
        bottom_fractals = [f for f in fractals if f.type.value == "bottom"]

        # 顶分型
        if top_fractals:
            top_indices = [f.index for f in top_fractals]
            top_prices = [f.price for f in top_fractals]

            # 应用索引映射
            if index_map:
                top_indices = [index_map.get(idx, idx) for idx in top_indices]

            ax.scatter(
                top_indices,
                top_prices,
                color=self.colors["top_fractal"],
                marker="v",
                s=120,
                label="顶分型",
                zorder=5,
                edgecolors="black",
            )

            # 添加价格标签
            for idx, price in zip(top_indices, top_prices):
                ax.annotate(
                    f"{price:.2f}",
                    (idx, price),
                    xytext=(0, 10),
                    textcoords="offset points",
                    fontsize=9,
                    color=self.colors["top_fractal"],
                    ha="center",
                    va="bottom",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
                )

        # 底分型
        if bottom_fractals:
            bottom_indices = [f.index for f in bottom_fractals]
            bottom_prices = [f.price for f in bottom_fractals]

            # 应用索引映射
            if index_map:
                bottom_indices = [index_map.get(idx, idx) for idx in bottom_indices]

            ax.scatter(
                bottom_indices,
                bottom_prices,
                color=self.colors["bottom_fractal"],
                marker="^",
                s=120,
                label="底分型",
                zorder=5,
                edgecolors="black",
            )

            # 添加价格标签
            for idx, price in zip(bottom_indices, bottom_prices):
                ax.annotate(
                    f"{price:.2f}",
                    (idx, price),
                    xytext=(0, -15),
                    textcoords="offset points",
                    fontsize=9,
                    color=self.colors["bottom_fractal"],
                    ha="center",
                    va="top",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
                )

    def _plot_strokes_detailed(self, ax, df, strokes, index_map=None):
        """详细绘制笔 - 修复版"""
        if not strokes:
            return

        for i, stroke in enumerate(strokes):
            start_idx = stroke.start_index
            end_idx = stroke.end_index
            start_price = stroke.start_price
            end_price = stroke.end_price

            # 应用索引映射
            if index_map:
                start_idx = index_map.get(start_idx, start_idx)
                end_idx = index_map.get(end_idx, end_idx)

            # 修复：确保索引在有效范围内
            start_idx = max(0, min(start_idx, len(df) - 1))
            end_idx = max(0, min(end_idx, len(df) - 1))

            color = (
                self.colors["up_stroke"]
                if stroke.direction == 1
                else self.colors["down_stroke"]
            )
            linewidth = 3 if i == len(strokes) - 1 else 2  # 最后一笔加粗

            ax.plot(
                [start_idx, end_idx],
                [start_price, end_price],
                color=color,
                linewidth=linewidth,
                alpha=0.8,
            )

            # 添加笔的标签
            mid_idx = (start_idx + end_idx) / 2
            mid_price = (start_price + end_price) / 2
            direction_text = "↑" if stroke.direction == 1 else "↓"

            ax.annotate(
                f"{direction_text} {abs(end_price-start_price):.2f}",
                (mid_idx, mid_price),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
                color=color,
                fontweight="bold",
            )

    def _plot_centrals_detailed(self, ax, df, centrals, index_map=None):
        """详细绘制中枢 - 修复版"""
        if not centrals:
            return

        for i, central in enumerate(centrals):
            start_idx = central.start_index
            end_idx = central.end_index
            high_price = central.high
            low_price = central.low

            # 应用索引映射
            if index_map:
                start_idx = index_map.get(start_idx, start_idx)
                end_idx = index_map.get(end_idx, end_idx)

            # 修复：确保索引在有效范围内
            start_idx = max(0, min(start_idx, len(df) - 1))
            end_idx = max(0, min(end_idx, len(df) - 1))

            color = self.colors["central"]

            # 绘制中枢矩形
            width = end_idx - start_idx
            height = high_price - low_price
            rect = Rectangle(
                (start_idx, low_price),
                width,
                height,
                facecolor=self.colors["central_fill"],
                alpha=0.4,
                edgecolor=color,
                linewidth=2,
                linestyle="--",
            )
            ax.add_patch(rect)

            # 添加中枢详细信息
            mid_idx = start_idx + width / 2
            mid_price = (high_price + low_price) / 2

            info_text = (
                f"中枢{i+1}\n{low_price:.2f}-{high_price:.2f}\n区间:{height:.2f}"
            )

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

    def _calculate_macd(self, df, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        close = df["close"]

        # 计算EMA
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()

        # MACD线
        macd_line = ema_fast - ema_slow

        # 信号线
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # 柱状图
        histogram = macd_line - signal_line

        return {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram,
        }

    def _plot_macd(self, ax, df, macd_result, divergences):
        """绘制MACD指标图"""
        dates = pd.to_datetime(df["time_key"])
        # 获取MACD数据
        macd_line = macd_result["macd_line"]
        signal_line = macd_result["signal_line"]
        histogram = macd_result["histogram"]

        # 绘制MACD线
        ax.plot(range(len(dates)), macd_line, label="MACD", color="blue", linewidth=1.5)
        ax.plot(
            range(len(dates)), signal_line, label="Signal", color="red", linewidth=1.5
        )

        # 绘制柱状图
        colors = ["red" if h >= 0 else "green" for h in histogram]
        ax.bar(range(len(dates)), histogram, color=colors, alpha=0.6, width=0.8)

        # 标记背驰位置
        # 创建索引映射，将DataFrame索引映射到绘图位置
        index_map = {idx: i for i, idx in enumerate(df.index)}

        for div in divergences:
            # 转换索引以匹配绘图位置
            idx = (
                div["price_index"]
                if div["price_index"] < len(df)
                else div["price_index"]
            )
            # 修复索引处理
            idx_mapped = index_map.get(idx, idx)
            if idx_mapped is not None:
                idx = int(idx_mapped)

            # 确保索引在有效范围内
            if idx >= len(dates) or idx >= len(macd_line):
                continue

            ax.axvline(x=idx, color="orange", linestyle="--", alpha=0.7, linewidth=1)
            # 转换索引以匹配绘图位置
            macd_idx = (
                div["price_index"]
                if div["price_index"] < len(df)
                else div["price_index"]
            )
            # 修复索引处理
            macd_idx_mapped = index_map.get(macd_idx, macd_idx)
            if macd_idx_mapped is not None:
                macd_idx = int(macd_idx_mapped)

            # 确保MACD索引在有效范围内
            if macd_idx < len(macd_line):
                ax.annotate(
                    div["type"],
                    (idx, macd_line.iloc[macd_idx]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=10,
                    color="orange",
                    fontweight="bold",
                )

        ax.set_ylabel("MACD", fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)

    def _plot_divergences(self, ax, df, divergences, index_map=None):
        """标记背驰信号"""
        # 创建索引映射，将DataFrame索引映射到绘图位置
        df_index_map = {idx: i for i, idx in enumerate(df.index)}

        for div in divergences:
            # 转换索引以匹配绘图位置
            idx = (
                div["price_index"]
                if div["price_index"] < len(df)
                else div["price_index"]
            )
            # 修复索引处理
            idx_mapped = df_index_map.get(idx, idx)
            if idx_mapped is not None:
                idx = int(idx_mapped)

            # 应用索引映射（从原始索引到合并后索引）
            if index_map:
                idx = index_map.get(idx, idx)

            price = div["price"]
            div_type = div["type"]

            # 背驰标记 - 使用matplotlib支持的箭头标记
            marker = "v" if "顶背驰" in div_type else "^"  # 使用v和^代替↓和↑
            color = "red" if "顶背驰" in div_type else "green"

            ax.scatter(idx, price, color=color, marker=marker, s=200, zorder=6)
            ax.annotate(
                f"{div_type}\n{price:.2f}",
                (idx, price),
                xytext=(10, 20 if "顶背驰" in div_type else -30),
                textcoords="offset points",
                fontsize=9,
                color=color,
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor=color,
                    alpha=0.2,
                    edgecolor=color,
                ),
            )


def generate_divergence_chart(
    stock_code, period="2y", interval="1d", save_dir="./chanlun_reports"
):
    """生成缠论背驰分析图表（仅PNG）"""

    print(f"正在生成 {stock_code} 的背驰分析图表...")

    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    try:
        # 获取数据 - 使用约360根K线
        data = get_stock_data(stock_code, period=period, interval=interval)

        if len(data) < 360:
            print(f"当前{len(data)}根K线，建议至少有360根K线进行完整分析")
            return

        # 缠论分析
        processor = ChanlunProcessor()
        result = processor.process(data)

        if result is None:
            print("缠论分析失败，返回空结果")
            return None

        # 将合并后的数据添加到结果中
        if hasattr(processor, "merged_df") and processor.merged_df is not None:
            result["merged_df"] = processor.merged_df
        else:
            result["merged_df"] = data

        # 创建可视化器
        visualizer = AdvancedChanlunVisualizer()

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存背驰分析图表
        chart_path = os.path.join(save_dir, f"{stock_code}_{timestamp}_divergence.png")
        visualizer.create_comprehensive_chart(data, result, stock_code, chart_path)

        print(f"\n=== {stock_code} 背驰分析图表生成完成 ===")
        print(f"背驰图表: {chart_path}")

        # 安全获取结果统计
        fractals_count = (
            len(result.get("fractals", []))
            if result and isinstance(result, dict)
            else 0
        )
        strokes_count = (
            len(result.get("strokes", [])) if result and isinstance(result, dict) else 0
        )
        centrals_count = (
            len(result.get("centrals", []))
            if result and isinstance(result, dict)
            else 0
        )

        print(f"分形: {fractals_count} | 笔: {strokes_count} | 中枢: {centrals_count}")

        return chart_path

    except Exception as e:
        print(f"生成背驰图表失败: {e}")
        return None


def batch_divergence_charts(stock_list=None, save_dir="./chanlun_reports"):
    """批量生成背驰分析图表"""

    if stock_list is None:
        stock_list = ["0700.HK", "0941.HK", "0005.HK", "0992.HK", "0016.HK"]

    print("开始批量生成缠论背驰分析图表...")

    for stock in stock_list:
        try:
            print(f"\n处理 {stock}...")
            generate_divergence_chart(stock, save_dir=save_dir)
            print("-" * 50)
        except Exception as e:
            print(f"处理 {stock} 时出错: {e}")
            continue

    print(f"\n批量生成完成！共处理 {len(stock_list)} 只股票")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
        generate_divergence_chart(stock_code)
    else:
        # 批量处理
        stock_list = ["0700.HK", "0941.HK", "0005.HK", "0992.HK", "0016.HK"]
        for stock in stock_list:
            generate_divergence_chart(stock)
