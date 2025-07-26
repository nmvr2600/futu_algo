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
from typing import Optional, Dict, List, Any
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
            "up_segment": "#ff4757",
            "down_segment": "#2ed573",
            "top_fractal": "#d62728",
            "bottom_fractal": "#2ca02c",
            "central": "#9467bd",
            "central_fill": "#e6e6fa",
            "bullish": "#26a69a",
            "bearish": "#ef5350",
        }

    def _create_index_map(self, df):
        """创建统一的索引映射，将DataFrame索引映射到绘图位置"""
        return {idx: i for i, idx in enumerate(df.index)}

    def _create_merged_index_map(self, result):
        """创建合并数据到原始数据的索引映射"""
        index_mapping = result.get("index_mapping", {})
        merged_index_map = {}

        # 为每个合并后的索引创建到原始索引的映射
        for merged_idx, original_indices in index_mapping.items():
            # 使用第一个原始索引作为代表
            if original_indices:
                merged_index_map[merged_idx] = original_indices[0]

        return merged_index_map

    def _create_fractal_number_map(self, result):
        """创建统一的分形编号映射"""
        # 收集所有分形索引
        all_fractal_indices = set()

        # 从分形中收集索引
        if "fractals" in result:
            for fractal in result["fractals"]:
                all_fractal_indices.add(fractal.index)

        # 从笔中收集索引
        if "strokes" in result:
            for stroke in result["strokes"]:
                all_fractal_indices.add(stroke.start_index)
                all_fractal_indices.add(stroke.end_index)

        # 从线段中收集索引
        if "segments" in result:
            for segment in result["segments"]:
                all_fractal_indices.add(segment.start_index)
                all_fractal_indices.add(segment.end_index)

        # 为分形创建编号映射，按索引排序
        fractal_number_map = {
            idx: i + 1 for i, idx in enumerate(sorted(all_fractal_indices))
        }
        return fractal_number_map

    def create_comprehensive_chart(self, df, result, stock_code, save_path=None):
        """创建缠论背驰分析图表"""
        fig = plt.figure(figsize=(20, 10))

        # 创建子图布局 - 主图和MACD副图
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)

        # 主K线图
        ax1 = fig.add_subplot(gs[0])
        # MACD副图
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        # 转换时间格式
        df = df.sort_values("time_key").reset_index(drop=True)
        dates = pd.to_datetime(df["time_key"])

        # 创建索引映射
        index_map = self._create_index_map(df)
        merged_index_map = self._create_merged_index_map(result)

        # 计算MACD
        macd_result = self._calculate_macd(df)

        # 识别背驰
        divergences = self._identify_divergences(
            df, result, macd_result, index_map, merged_index_map
        )

        # 绘制主图表
        self._plot_enhanced_kline(
            ax1, df, dates, result, divergences, index_map, merged_index_map
        )
        self._plot_macd(
            ax2, df, dates, macd_result, divergences, index_map, merged_index_map
        )

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

    def _calculate_macd_area(self, histogram, start_idx, end_idx):
        """计算MACD柱状图面积，分别计算红柱和绿柱面积"""
        if start_idx >= len(histogram) or end_idx >= len(histogram):
            return {"red": 0, "green": 0}
        
        # 确保start_idx <= end_idx
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
            
        # 分别计算红柱和绿柱面积
        red_area = 0  # 红柱面积（正值）
        green_area = 0  # 绿柱面积（负值的绝对值）
        
        for i in range(start_idx, end_idx + 1):
            if i < len(histogram):
                if histogram.iloc[i] >= 0:
                    red_area += histogram.iloc[i]
                else:
                    green_area += abs(histogram.iloc[i])
        
        return {"red": red_area, "green": green_area}

    def _identify_divergences(
        self, df, result, macd_result, index_map, merged_index_map
    ):
        """识别背驰信号"""
        divergences = []

        # 获取笔数据
        strokes = result["strokes"]
        if len(strokes) < 3:  # 至少需要3笔才能判断背驰
            return divergences

        # 获取MACD数据
        macd_line = macd_result["macd_line"]
        signal_line = macd_result["signal_line"]
        histogram = macd_result["histogram"]

        # 获取中枢数据
        centrals = result["centrals"]

        # 检查相邻笔之间的背驰
        # 首先找出所有同向的笔段
        up_strokes = []  # 上涨笔段
        down_strokes = []  # 下跌笔段
        
        for i, stroke in enumerate(strokes):
            if stroke.direction == 1:  # 上涨笔
                up_strokes.append((i, stroke))
            else:  # 下跌笔
                down_strokes.append((i, stroke))
        
        # 检查上涨笔段之间的顶背驰
        for i in range(1, len(up_strokes)):
            current_idx, current_stroke = up_strokes[i]
            prev_idx, prev_stroke = up_strokes[i-1]
            
            # 顶背驰：价格创新高，但MACD红柱面积减小
            if current_stroke.end_price > prev_stroke.end_price:
                # 获取笔段的起始和结束索引
                current_start_idx = current_stroke.start_index
                current_end_idx = current_stroke.end_index
                prev_start_idx = prev_stroke.start_index
                prev_end_idx = prev_stroke.end_index
                
                # 应用合并索引映射
                if merged_index_map:
                    current_start_idx = merged_index_map.get(current_start_idx, current_start_idx)
                    current_end_idx = merged_index_map.get(current_end_idx, current_end_idx)
                    prev_start_idx = merged_index_map.get(prev_start_idx, prev_start_idx)
                    prev_end_idx = merged_index_map.get(prev_end_idx, prev_end_idx)

                # 应用索引映射
                if index_map:
                    current_start_idx = index_map.get(current_start_idx, current_start_idx)
                    current_end_idx = index_map.get(current_end_idx, current_end_idx)
                    prev_start_idx = index_map.get(prev_start_idx, prev_start_idx)
                    prev_end_idx = index_map.get(prev_end_idx, prev_end_idx)
                
                # 计算前一段的MACD面积
                prev_area = self._calculate_macd_area(histogram, prev_start_idx, prev_end_idx)
                # 计算当前段的MACD面积
                current_area = self._calculate_macd_area(histogram, current_start_idx, current_end_idx)
                
                # 顶背驰判断：当前红柱面积小于前次
                if current_area["red"] < prev_area["red"]:
                    # 判断是否在中枢内
                    in_central = False
                    for central in centrals:
                        if (central.start_index <= current_stroke.end_index <= central.end_index) or \
                           (central.start_index <= prev_stroke.end_index <= central.end_index):
                            in_central = True
                            break
                    
                    if in_central:
                        divergence_type = "盘整顶背驰"
                    else:
                        divergence_type = "趋势顶背驰"
                    
                    # 获取MACD值
                    current_macd = (
                        macd_line.iloc[current_end_idx]
                        if current_end_idx < len(macd_line)
                        else macd_line.iloc[-1]
                    )
                    
                    divergences.append(
                        {
                            "type": divergence_type,
                            "stroke_index": current_idx,
                            "price_index": current_stroke.end_index,
                            "price": current_stroke.end_price,
                            "macd_value": current_macd,
                            "macd_area": current_area,
                        }
                    )
        
        # 检查下跌笔段之间的底背驰
        for i in range(1, len(down_strokes)):
            current_idx, current_stroke = down_strokes[i]
            prev_idx, prev_stroke = down_strokes[i-1]
            
            # 底背驰：价格创新低，但MACD绿柱面积增大
            if current_stroke.end_price < prev_stroke.end_price:
                # 获取笔段的起始和结束索引
                current_start_idx = current_stroke.start_index
                current_end_idx = current_stroke.end_index
                prev_start_idx = prev_stroke.start_index
                prev_end_idx = prev_stroke.end_index
                
                # 应用合并索引映射
                if merged_index_map:
                    current_start_idx = merged_index_map.get(current_start_idx, current_start_idx)
                    current_end_idx = merged_index_map.get(current_end_idx, current_end_idx)
                    prev_start_idx = merged_index_map.get(prev_start_idx, prev_start_idx)
                    prev_end_idx = merged_index_map.get(prev_end_idx, prev_end_idx)

                # 应用索引映射
                if index_map:
                    current_start_idx = index_map.get(current_start_idx, current_start_idx)
                    current_end_idx = index_map.get(current_end_idx, current_end_idx)
                    prev_start_idx = index_map.get(prev_start_idx, prev_start_idx)
                    prev_end_idx = index_map.get(prev_end_idx, prev_end_idx)
                
                # 计算前一段的MACD面积
                prev_area = self._calculate_macd_area(histogram, prev_start_idx, prev_end_idx)
                # 计算当前段的MACD面积
                current_area = self._calculate_macd_area(histogram, current_start_idx, current_end_idx)
                
                # 底背驰判断：当前绿柱面积大于前次
                if current_area["green"] > prev_area["green"]:
                    # 判断是否在中枢内
                    in_central = False
                    for central in centrals:
                        if (central.start_index <= current_stroke.end_index <= central.end_index) or \
                           (central.start_index <= prev_stroke.end_index <= central.end_index):
                            in_central = True
                            break
                    
                    if in_central:
                        divergence_type = "盘整底背驰"
                    else:
                        divergence_type = "趋势底背驰"
                    
                    # 获取MACD值
                    current_macd = (
                        macd_line.iloc[current_end_idx]
                        if current_end_idx < len(macd_line)
                        else macd_line.iloc[-1]
                    )
                    
                    divergences.append(
                        {
                            "type": divergence_type,
                            "stroke_index": current_idx,
                            "price_index": current_stroke.end_index,
                            "price": current_stroke.end_price,
                            "macd_value": current_macd,
                            "macd_area": current_area,
                        }
                    )

        return divergences

    def _plot_enhanced_kline(
        self, ax, df, dates, result, divergences, index_map, merged_index_map
    ):
        """绘制增强版K线图，包含背驰标记"""
        # 绘制K线
        for i, (date, row) in enumerate(zip(dates, df.itertuples())):
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
            ax.plot([i, i], [low_price, high_price], color=color, linewidth=1)

        # 创建分形编号映射
        fractal_number_map = self._create_fractal_number_map(result)

        # 绘制分形
        self._plot_fractals_detailed(
            ax, df, result["fractals"], index_map, fractal_number_map, merged_index_map
        )

        # 绘制笔
        self._plot_strokes_detailed(
            ax, df, result["strokes"], index_map, fractal_number_map, merged_index_map
        )

        # 绘制线段
        self._plot_segments_detailed(
            ax, df, result["segments"], index_map, fractal_number_map, merged_index_map
        )

        # 绘制中枢
        self._plot_centrals_detailed(
            ax, df, result["centrals"], index_map, merged_index_map
        )

        # 标记背驰信号
        self._plot_divergences(ax, df, divergences, index_map, merged_index_map)

        # 设置网格和标签
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_ylabel("价格", fontsize=12)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))

        # 价格格式化
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.2f}"))

    def _plot_fractals_detailed(
        self,
        ax,
        df,
        fractals,
        index_map=None,
        fractal_number_map=None,
        merged_index_map=None,
    ):
        """详细绘制分形"""
        if not fractals:
            return

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
                color=self.colors["top_fractal"],
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
                    color=self.colors["top_fractal"],
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
                        facecolor=self.colors["top_fractal"],
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
                bottom_indices = [
                    merged_index_map.get(idx, idx) for idx in bottom_indices
                ]

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

            # 添加价格标签和编号
            for idx, price, number in zip(
                bottom_indices, bottom_prices, bottom_numbers
            ):
                # 价格标签
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
                        facecolor=self.colors["bottom_fractal"],
                        alpha=0.9,
                        edgecolor="black",
                    ),
                )

    def _plot_strokes_detailed(
        self,
        ax,
        df,
        strokes,
        index_map=None,
        fractal_number_map=None,
        merged_index_map=None,
    ):
        """详细绘制笔 - 连接不连续索引"""
        if not strokes:
            return

        for i, stroke in enumerate(strokes):
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

            color = (
                self.colors["up_stroke"]
                if stroke.direction == 1
                else self.colors["down_stroke"]
            )
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
                fractal_number_map.get(stroke.end_index, "?")
                if fractal_number_map
                else "?"
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

    def _plot_segments_detailed(
        self,
        ax,
        df,
        segments,
        index_map=None,
        fractal_number_map=None,
        merged_index_map=None,
    ):
        """详细绘制线段"""
        if not segments:
            return

        for i, segment in enumerate(segments):
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
            color = (
                self.colors["up_segment"]
                if direction == 1
                else self.colors["down_segment"]
            )

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

    def _plot_centrals_detailed(
        self, ax, df, centrals, index_map=None, merged_index_map=None
    ):
        """详细绘制中枢"""
        if not centrals:
            return

        for i, central in enumerate(centrals):
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

            high_price = central.high
            low_price = central.low

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

    def _plot_macd(
        self, ax, df, dates, macd_result, divergences, index_map, merged_index_map=None
    ):
        """绘制MACD指标图"""
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

        for div in divergences:
            # 转换索引以匹配绘图位置
            idx = div["price_index"]

            # 应用合并索引映射
            if merged_index_map:
                idx = merged_index_map.get(idx, idx)

            # 应用索引映射
            if index_map:
                idx = index_map.get(idx, idx)

            ax.axvline(x=idx, color="orange", linestyle="--", alpha=0.7, linewidth=1)
            # 转换索引以匹配绘图位置
            macd_idx = div["price_index"]

            # 应用合并索引映射
            if merged_index_map:
                macd_idx = merged_index_map.get(macd_idx, macd_idx)

            # 应用索引映射
            if index_map:
                macd_idx = index_map.get(macd_idx, macd_idx)

            macd_value = (
                macd_line.iloc[macd_idx]
                if macd_idx < len(macd_line)
                else macd_line.iloc[-1]
            )
            ax.annotate(
                div["type"],
                (idx, macd_value),
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

    def _plot_divergences(self, ax, df, divergences, index_map, merged_index_map=None):
        """标记背驰信号"""
        for div in divergences:
            # 转换索引以匹配绘图位置
            idx = div["price_index"]

            # 应用合并索引映射
            if merged_index_map:
                idx = merged_index_map.get(idx, idx)

            # 应用索引映射
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
    stock_code,
    period="2y",
    interval="1d",
    kline_count=None,
    save_dir="./chanlun_reports",
):
    """生成缠论背驰分析图表（仅PNG）

    Args:
        stock_code: 股票代码
        period: 时间段 ('1y', '2y', '6mo', etc.)
        interval: 时间间隔 ('1d', '1wk', etc.)
        kline_count: 指定使用的K线数量
        save_dir: 保存目录
    """

    print(f"正在生成 {stock_code} 的背驰分析图表...")

    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    try:
        # 获取数据
        data = get_stock_data(stock_code, period=period, interval=interval)

        # 如果指定了K线数量，则截取相应数量的K线
        if kline_count is not None and kline_count > 0:
            data = data.tail(kline_count).reset_index(drop=True)
            print(f"使用最近 {len(data)} 根K线进行分析")

        if len(data) < 30:
            print(f"当前{len(data)}根K线，数据不足无法进行完整分析")
            return

        # 缠论分析
        processor = ChanlunProcessor()
        result = processor.process(data)

        # 创建可视化器
        visualizer = AdvancedChanlunVisualizer()

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存背驰分析图表
        chart_path = os.path.join(save_dir, f"{stock_code}_{timestamp}_divergence.png")
        visualizer.create_comprehensive_chart(data, result, stock_code, chart_path)

        print(f"\n=== {stock_code} 背驰分析图表生成完成 ===")
        print(f"背驰图表: {chart_path}")
        print(
            f"分形: {len(result['fractals'])} | 笔: {len(result['strokes'])} | 中枢: {len(result['centrals'])}"
        )

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
