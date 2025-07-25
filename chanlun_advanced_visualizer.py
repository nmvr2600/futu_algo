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

    def _create_index_mapping(self, merged_df, original_df):
        """创建从合并后索引到原始索引的映射"""
        if merged_df is None or merged_df.empty:
            return {}

        # 创建映射字典
        index_map = {}

        # 遍历合并后的数据，建立映射关系
        for merged_idx, row in merged_df.iterrows():
            if "original_indices" in row:
                original_indices = row["original_indices"]
                # 使用每个合并K线对应原始K线的最后一个索引作为代表
                if original_indices:
                    index_map[merged_idx] = original_indices[-1]

        return index_map

    def create_comprehensive_chart(self, df, result, stock_code, save_path=None):
        """创建缠论背驰分析图表"""
        fig = plt.figure(figsize=(20, 12))  # 增加图表高度

        # 创建子图布局 - 主图和MACD副图
        gs = fig.add_gridspec(
            2, 1, height_ratios=[4, 1], hspace=0.1
        )  # 调整高度比例和间距

        # 主K线图
        ax1 = fig.add_subplot(gs[0])
        # MACD副图
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        # 使用原始df的dates
        dates = pd.to_datetime(df["time_key"])

        # 创建索引映射：从合并后索引映射到原始索引
        index_map = self._create_index_mapping(result.get("merged_df", df), df)

        # 计算MACD (必须使用原始数据 df)
        macd_result = self._calculate_macd(df)

        # 识别背驰 (使用原始df计算的MACD)
        divergences = self._identify_divergences(df, result, macd_result)

        # 绘制主图表
        self._plot_enhanced_kline(ax1, df, dates, result, divergences, index_map)
        self._plot_macd(ax2, df, macd_result, divergences, index_map)

        # 设置标题
        fig.suptitle(
            f"{stock_code} - 缠论背驰分析\n"
            f'分形:{len(result["fractals"])} | '
            f'笔:{len(result["strokes"])} | '
            f'中枢:{len(result["centrals"])} | '
            f"背驰:{len(divergences)}",
            fontsize=16,
            fontweight="bold",
            y=0.95,  # 调整标题位置
        )

        # 调整布局
        plt.tight_layout(rect=(0, 0, 0.85, 0.95))  # 为图例和标题留出空间

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
            print(f"背驰分析图表已保存到: {save_path}")

        return fig

    def _identify_divergences(self, df, result, macd_result):
        """识别背驰信号 - 缠论标准背驰判断"""
        divergences = []

        # 获取笔数据
        strokes = result["strokes"]
        centrals = result["centrals"]

        if len(strokes) < 3:
            return divergences

        # 获取MACD数据
        macd_line = macd_result["macd_line"]
        histogram = macd_result["histogram"]

        # 1. 趋势背驰判断（需要至少两个中枢，如果没有则尝试用笔构建趋势段）
        if len(centrals) >= 2:
            trend_divergences = self._identify_trend_divergence(
                strokes, centrals, macd_line, histogram
            )
            divergences.extend(trend_divergences)
        else:
            # 如果没有足够的中枢，使用笔来构建趋势段进行背驰判断
            trend_divergences = self._identify_trend_divergence_by_strokes(
                strokes, macd_line, histogram
            )
            divergences.extend(trend_divergences)

        # 2. 盘整背驰判断（中枢内部，如果没有中枢则跳过）
        if len(centrals) >= 1:
            range_divergences = self._identify_range_divergence(
                strokes, centrals[-1], macd_line, histogram
            )
            divergences.extend(range_divergences)

        # 3. 笔间背驰判断（相邻笔）
        stroke_divergences = self._identify_stroke_divergence(
            strokes, macd_line, histogram
        )
        divergences.extend(stroke_divergences)

        return divergences

    def _identify_trend_divergence(self, strokes, centrals, macd_line, histogram):
        """识别趋势背驰 - 基于缠论标准"""
        divergences = []

        # 至少需要两个中枢才能判断趋势背驰
        if len(centrals) < 2 or len(strokes) < 6:
            return divergences

        # 获取最后两个中枢
        last_central = centrals[-1]
        prev_central = centrals[-2]

        # 找到离开前一个中枢和最后一个中枢的笔
        # 离开前一个中枢的笔
        exit_prev_strokes = [
            s
            for s in strokes
            if s.start_index > prev_central.end_index
            and s.start_index <= last_central.start_index
        ]
        # 离开最后一个中枢的笔
        exit_last_strokes = [
            s for s in strokes if s.start_index > last_central.end_index
        ]

        if len(exit_prev_strokes) < 2 or len(exit_last_strokes) < 2:
            return divergences

        # 计算前一个趋势段的MACD面积
        prev_start_idx = exit_prev_strokes[0].start_index
        prev_end_idx = exit_prev_strokes[-1].end_index
        prev_macd_area = self._calculate_macd_area(
            histogram, prev_start_idx, prev_end_idx
        )

        # 计算最后一个趋势段的MACD面积
        last_start_idx = exit_last_strokes[0].start_index
        last_end_idx = exit_last_strokes[-1].end_index
        last_macd_area = self._calculate_macd_area(
            histogram, last_start_idx, last_end_idx
        )

        # 获取价格信息
        prev_price_high = max(s.end_price for s in exit_prev_strokes)
        last_price_high = max(s.end_price for s in exit_last_strokes)

        # 趋势背驰条件：
        # 1. 价格创新高
        # 2. MACD力度减弱（面积变小）
        if prev_macd_area != 0 and last_macd_area != 0:
            if (
                last_price_high > prev_price_high
                and abs(last_macd_area) < abs(prev_macd_area) * 0.8
            ):
                divergences.append(
                    {
                        "type": "趋势顶背驰",
                        "price_index": exit_last_strokes[-1].end_index,
                        "price": exit_last_strokes[-1].end_price,
                        "macd_area_ratio": abs(last_macd_area / prev_macd_area),
                        "strength": "strong",
                    }
                )

        # 检查底背驰
        prev_price_low = min(s.end_price for s in exit_prev_strokes)
        last_price_low = min(s.end_price for s in exit_last_strokes)

        if prev_macd_area != 0 and last_macd_area != 0:
            if (
                last_price_low < prev_price_low
                and abs(last_macd_area) < abs(prev_macd_area) * 0.8
            ):
                divergences.append(
                    {
                        "type": "趋势底背驰",
                        "price_index": exit_last_strokes[-1].end_index,
                        "price": exit_last_strokes[-1].end_price,
                        "macd_area_ratio": abs(last_macd_area / prev_macd_area),
                        "strength": "strong",
                    }
                )

        return divergences

    def _identify_range_divergence(self, strokes, central, macd_line, histogram):
        """识别盘整背驰 - 基于缠论标准"""
        divergences = []

        # 在中枢内部寻找背驰
        central_strokes = [
            s
            for s in strokes
            if s.start_index >= central.start_index and s.end_index <= central.end_index
        ]

        if len(central_strokes) < 4:  # 至少需要4笔才能形成有效的盘整背驰
            return divergences

        # 将中枢内的笔分为前后两段
        mid_point = len(central_strokes) // 2
        first_half = central_strokes[:mid_point]
        second_half = central_strokes[mid_point:]

        if len(first_half) < 2 or len(second_half) < 2:
            return divergences

        # 计算前后两段的MACD面积
        first_start = first_half[0].start_index
        first_end = first_half[-1].end_index
        second_start = second_half[0].start_index
        second_end = second_half[-1].end_index

        first_macd_area = self._calculate_macd_area(histogram, first_start, first_end)
        second_macd_area = self._calculate_macd_area(
            histogram, second_start, second_end
        )

        # 获取价格信息
        first_high = max(s.end_price for s in first_half)
        first_low = min(s.end_price for s in first_half)
        second_high = max(s.end_price for s in second_half)
        second_low = min(s.end_price for s in second_half)

        # 盘整顶背驰：价格创新高但MACD力度减弱
        if first_macd_area != 0 and second_macd_area != 0:
            if (
                second_high > first_high
                and abs(second_macd_area) < abs(first_macd_area) * 0.7
            ):
                divergences.append(
                    {
                        "type": "盘整顶背驰",
                        "price_index": second_half[-1].end_index,
                        "price": second_half[-1].end_price,
                        "macd_area_ratio": abs(second_macd_area / first_macd_area),
                        "strength": "medium",
                    }
                )

        # 盘整底背驰：价格创新低但MACD力度减弱
        if first_macd_area != 0 and second_macd_area != 0:
            if (
                second_low < first_low
                and abs(second_macd_area) < abs(first_macd_area) * 0.7
            ):
                divergences.append(
                    {
                        "type": "盘整底背驰",
                        "price_index": second_half[-1].end_index,
                        "price": second_half[-1].end_price,
                        "macd_area_ratio": abs(second_macd_area / first_macd_area),
                        "strength": "medium",
                    }
                )

        return divergences

    def _identify_stroke_divergence(self, strokes, macd_line, histogram):
        """识别笔间背驰 - 基于缠论标准"""
        divergences = []

        if len(strokes) < 4:  # 至少需要4笔
            return divergences

        # 检查相邻笔之间的背驰（检查最后几组笔）
        for i in range(max(2, len(strokes) - 4), len(strokes) - 1):
            prev_stroke = strokes[i - 1]
            curr_stroke = strokes[i]

            # 确保笔的方向相反
            if prev_stroke.direction == curr_stroke.direction:
                continue

            # 计算两笔的MACD面积
            prev_area = self._calculate_macd_area(
                histogram, prev_stroke.start_index, prev_stroke.end_index
            )
            curr_area = self._calculate_macd_area(
                histogram, curr_stroke.start_index, curr_stroke.end_index
            )

            # 顶背驰：价格上涨但MACD力度减弱（降低阈值以提高敏感性）
            if curr_stroke.direction == 1:  # 当前笔向上
                price_condition = curr_stroke.end_price > prev_stroke.end_price
                macd_condition = (
                    prev_area != 0
                    and curr_area != 0
                    and abs(curr_area) < abs(prev_area) * 0.9
                )

                # 添加调试信息
                # print(f"笔间顶背驰检查: 价格条件={price_condition}, MACD条件={macd_condition}")
                # print(f"  当前笔价格: {prev_stroke.end_price:.2f} -> {curr_stroke.end_price:.2f}")
                # print(f"  MACD面积: {abs(prev_area):.2f} -> {abs(curr_area):.2f}")

                if price_condition and macd_condition:
                    divergences.append(
                        {
                            "type": "笔间顶背驰",
                            "stroke_index": i,
                            "price_index": curr_stroke.end_index,
                            "price": curr_stroke.end_price,
                            "macd_area_ratio": (
                                abs(curr_area / prev_area) if prev_area != 0 else 0
                            ),
                            "strength": "weak",
                        }
                    )
            else:  # 当前笔向下
                # 底背驰：价格下跌但MACD力度减弱（降低阈值以提高敏感性）
                price_condition = curr_stroke.end_price < prev_stroke.end_price
                macd_condition = (
                    prev_area != 0
                    and curr_area != 0
                    and abs(curr_area) < abs(prev_area) * 0.9
                )

                # 添加调试信息
                # print(f"笔间底背驰检查: 价格条件={price_condition}, MACD条件={macd_condition}")
                # print(f"  当前笔价格: {prev_stroke.end_price:.2f} -> {curr_stroke.end_price:.2f}")
                # print(f"  MACD面积: {abs(prev_area):.2f} -> {abs(curr_area):.2f}")

                if price_condition and macd_condition:
                    divergences.append(
                        {
                            "type": "笔间底背驰",
                            "stroke_index": i,
                            "price_index": curr_stroke.end_index,
                            "price": curr_stroke.end_price,
                            "macd_area_ratio": (
                                abs(curr_area / prev_area) if prev_area != 0 else 0
                            ),
                            "strength": "weak",
                        }
                    )

        return divergences

    def _identify_trend_divergence_by_strokes(self, strokes, macd_line, histogram):
        """通过笔识别趋势背驰 - 当没有足够中枢时使用"""
        divergences = []

        if len(strokes) < 6:  # 至少需要6笔
            return divergences

        # 将笔分为前后两段，每段至少3笔
        mid_point = len(strokes) // 2
        if mid_point < 3 or (len(strokes) - mid_point) < 3:
            return divergences

        first_strokes = strokes[:mid_point]
        second_strokes = strokes[mid_point:]

        # 计算前后两段的MACD面积
        first_start = first_strokes[0].start_index
        first_end = first_strokes[-1].end_index
        second_start = second_strokes[0].start_index
        second_end = second_strokes[-1].end_index

        first_macd_area = self._calculate_macd_area(histogram, first_start, first_end)
        second_macd_area = self._calculate_macd_area(
            histogram, second_start, second_end
        )

        # 获取价格信息
        first_high = max(s.end_price for s in first_strokes)
        first_low = min(s.end_price for s in first_strokes)
        second_high = max(s.end_price for s in second_strokes)
        second_low = min(s.end_price for s in second_strokes)

        # 趋势顶背驰：价格创新高但MACD力度减弱（降低阈值以提高敏感性）
        if first_macd_area != 0 and second_macd_area != 0:
            if (
                second_high > first_high
                and abs(second_macd_area) < abs(first_macd_area) * 0.9
            ):
                divergences.append(
                    {
                        "type": "趋势顶背驰",
                        "price_index": second_strokes[-1].end_index,
                        "price": second_strokes[-1].end_price,
                        "macd_area_ratio": abs(second_macd_area / first_macd_area),
                        "strength": "strong",
                    }
                )

        # 趋势底背驰：价格创新低但MACD力度减弱（降低阈值以提高敏感性）
        if first_macd_area != 0 and second_macd_area != 0:
            price_condition = second_low < first_low
            macd_condition = abs(second_macd_area) < abs(first_macd_area) * 0.9

            # 添加调试信息
            # print(f"趋势底背驰检查: 价格条件={price_condition}, MACD条件={macd_condition}")
            # print(f"  价格: {first_low:.2f} -> {second_low:.2f}")
            # print(f"  MACD面积: {abs(first_macd_area):.2f} -> {abs(second_macd_area):.2f}")

            if price_condition and macd_condition:
                divergences.append(
                    {
                        "type": "趋势底背驰",
                        "price_index": second_strokes[-1].end_index,
                        "price": second_strokes[-1].end_price,
                        "macd_area_ratio": abs(second_macd_area / first_macd_area),
                        "strength": "strong",
                    }
                )

        return divergences

    def _calculate_macd_area(self, histogram, start_idx, end_idx):
        """计算MACD柱状图面积"""
        try:
            if start_idx >= len(histogram) or end_idx >= len(histogram):
                return 0

            area = 0
            for i in range(start_idx, min(end_idx + 1, len(histogram))):
                area += abs(histogram.iloc[i])
            return area
        except:
            return 0

    def _calculate_macd(self, df, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        if df.empty or "close" not in df.columns:
            # 返回空数据
            empty_series = pd.Series(dtype=float)
            return {
                "macd_line": empty_series,
                "signal_line": empty_series,
                "histogram": empty_series,
            }

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

    def _plot_enhanced_kline(self, ax, df, dates, result, divergences, index_map=None):
        """绘制增强版K线图，包含背驰标记"""
        # 使用原始df进行K线绘制，保持数据一致性
        for i in range(len(df)):
            row = df.iloc[i]
            open_price = row.open
            high_price = row.high
            low_price = row.low
            close_price = row.close

            color = (
                self.colors["bullish"]
                if close_price >= open_price
                else self.colors["bearish"]
            )

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
            ax.plot(
                [i, i],
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

        # 设置x轴范围，确保K线铺满整个图表空间
        ax.set_xlim(-1, len(df))

        # 设置x轴刻度和标签
        # 计算合适的刻度间隔
        x_ticks_interval = max(1, len(df) // 10)  # 大约显示10个刻度
        x_ticks = list(range(0, len(df), x_ticks_interval))
        ax.set_xticks(x_ticks)

        # 格式化x轴标签
        if len(dates) > 0:
            x_labels = [
                dates.iloc[i].strftime("%m/%d") if i < len(dates) else ""
                for i in x_ticks
            ]
            ax.set_xticklabels(x_labels, rotation=45, ha="right")

        # 设置网格和标签
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_ylabel("价格", fontsize=12)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))

        # 设置y轴范围，确保K线充分利用垂直空间
        if len(df) > 0:
            # 计算价格范围
            high_prices = df["high"].max()
            low_prices = df["low"].min()
            price_range = high_prices - low_prices

            # 添加一些边距
            margin = price_range * 0.05  # 5%的边距
            ax.set_ylim(low_prices - margin, high_prices + margin)

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

    def _plot_macd(self, ax, df, macd_result, divergences, index_map=None):
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
        for div in divergences:
            idx = div["price_index"]

            # 应用索引映射
            if index_map:
                idx = index_map.get(idx, idx)

            # 确保索引在有效范围内
            if idx >= len(df) or idx >= len(macd_line):
                continue

            ax.axvline(x=idx, color="orange", linestyle="--", alpha=0.7, linewidth=1)

            # 添加背驰标记
            ax.annotate(
                div["type"],
                (idx, macd_line.iloc[idx]),
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
        for div in divergences:
            idx = div["price_index"]

            # 应用索引映射
            if index_map:
                idx = index_map.get(idx, idx)

            # 确保索引在有效范围内
            if idx >= len(df):
                continue

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
