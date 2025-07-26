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
        # 确保df有连续的整数索引
        if len(df) == 0:
            return {}
        return {i: i for i in range(len(df))}

    def _create_merged_index_map(self, result):
        """创建合并数据到原始数据的索引映射"""
        index_mapping = result.get("index_mapping", {})
        merged_index_map = {}

        # 为每个合并后的索引创建到原始索引的映射
        for merged_idx, original_indices in index_mapping.items():
            # 使用第一个原始索引作为代表
            if original_indices:
                merged_index_map[merged_idx] = original_indices[0]

        # 添加索引映射验证
        print(f"索引映射验证 - 合并前索引数: {sum(len(indices) for indices in index_mapping.values())}, 合并后索引数: {len(merged_index_map)}")
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

        # 保存原始数据用于绘图
        original_df = df.copy()
        original_length = len(df)
        
        # 转换时间格式（使用原始数据进行绘图）
        df_for_plotting = df.sort_values("time_key").reset_index(drop=True)
        # 确保time_key列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df_for_plotting["time_key"]):
            dates = pd.to_datetime(df_for_plotting["time_key"])
        else:
            dates = df_for_plotting["time_key"]
        
        # 转换日期为数字格式用于绘图
        x_dates = [mdates.date2num(date) for date in dates]
        
        # 验证数据对齐
        print(f"数据对齐验证 - dates长度: {len(dates)}, x_dates长度: {len(x_dates)}, df长度: {len(df_for_plotting)}")
        
        # 确保x_dates和df长度一致
        if len(x_dates) != len(df_for_plotting):
            print(f"调整数据对齐 - 截取前x_dates: {len(x_dates)}, df: {len(df_for_plotting)}")
            min_length = min(len(x_dates), len(df_for_plotting))
            x_dates = x_dates[:min_length]
            df_for_plotting = df_for_plotting.iloc[:min_length].reset_index(drop=True)
            dates = dates[:min_length]
            print(f"调整后长度: {len(x_dates)}")

        # 创建索引映射
        index_map = self._create_index_map(df)
        merged_index_map = self._create_merged_index_map(result)

        # 计算MACD（使用原始数据）
        macd_result = self._calculate_macd(df_for_plotting)

        # 识别背驰
        divergences = self._identify_divergences(
            df_for_plotting, result, macd_result, index_map, merged_index_map
        )

        # 绘制主图表
        self._plot_enhanced_kline(
            fig, ax1, df_for_plotting, dates, x_dates, result, divergences, index_map, merged_index_map
        )
        self._plot_macd(
            ax2, df_for_plotting, dates, x_dates, macd_result, divergences, index_map, merged_index_map
        )
        
        # 根据数据间隔和密度智能调整x轴设置
        if len(dates) > 0:
            # 计算数据间隔
            if len(dates) > 1:
                avg_interval = (dates.iloc[-1] - dates.iloc[0]).total_seconds() / (len(dates) - 1)
            else:
                avg_interval = 86400  # 默认为1天
            
            # 根据间隔类型设置合适的格式
            if avg_interval < 3600:  # 小于1小时（分钟级数据）
                date_format = '%H:%M'
                # 使用更稀疏的刻度
                ax1.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(dates)//24)))
                # 调整K线宽度
                bar_width = 0.3 * (avg_interval / 3600)  # 根据实际间隔调整
            elif avg_interval < 86400:  # 小于1天（小时级数据）
                date_format = '%m-%d\n%H:%M'
                ax1.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(dates)//12)))
                bar_width = 0.4 * (avg_interval / 86400)
            elif avg_interval < 7 * 86400:  # 小于1周（日级数据）
                date_format = '%m-%d'
                ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
                bar_width = 0.6
            else:  # 周级或月级数据
                date_format = '%Y-%m-%d'
                ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
                bar_width = 0.6
        else:
            date_format = '%Y-%m-%d'
            bar_width = 0.6

        # 设置x轴格式
        ax1.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        ax1.set_xlim(x_dates[0], x_dates[-1])
        
        # 设置MACD子图的x轴
        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        ax2.set_xlim(x_dates[0], x_dates[-1])

        # 自动旋转日期标签
        fig.autofmt_xdate()

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

    def _plot_enhanced_kline(self, fig, ax, df, dates, x_dates, result, divergences, index_map, merged_index_map):
        """绘制增强版K线图，包含背驰标记"""
        if df.empty:
            return
            
        # 确保我们不会超出df的范围
        max_index = min(len(x_dates), len(df))
        if max_index == 0:
            return
            
        # 数据对齐检查
        if len(x_dates) != len(df):
            print(f"警告: x_dates和df长度不一致 - x_dates: {len(x_dates)}, df: {len(df)}")
            
        # 根据数据密度动态设置K线宽度
        if len(df) > 100:
            bar_width = 0.3  # 高密度数据使用较小宽度
        elif len(df) > 50:
            bar_width = 0.5  # 中等密度使用中等宽度
        else:
            bar_width = 0.6  # 低密度数据使用较大宽度
            
        # 统一绘制逻辑，不管dates和df是否长度一致
        for i in range(max_index):
            x_date = x_dates[i]
            row = df.iloc[i]
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            
            # 绘制影线
            ax.plot([x_date, x_date], [low_price, high_price], color='black', linewidth=1)

            # 绘制实体
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            
            # 根据涨跌情况设置不同的显示方式
            if close_price >= open_price:
                # 阳线（上涨）- 红色填充实体
                rect = Rectangle(
                    (x_date - bar_width/2, bottom),
                    bar_width,
                    height,
                    facecolor='red',
                    alpha=0.8,
                    edgecolor='black',
                )
            else:
                # 阴线（下跌）- 绿色填充实体
                rect = Rectangle(
                    (x_date - bar_width/2, bottom),
                    bar_width,
                    height,
                    facecolor='green',
                    alpha=0.8,
                    edgecolor='black',
                )
            
            ax.add_patch(rect)

        # 创建分形编号映射
        fractal_number_map = self._create_fractal_number_map(result)

        # 绘制分形
        self._plot_fractals_detailed(
            ax, df, dates, result["fractals"], index_map, fractal_number_map, merged_index_map
        )

        # 绘制笔
        self._plot_strokes_detailed(
            ax, df, dates, result["strokes"], index_map, fractal_number_map, merged_index_map
        )

        # 绘制线段
        self._plot_segments_detailed(
            ax, df, dates, result["segments"], index_map, fractal_number_map, merged_index_map
        )

        # 绘制中枢
        self._plot_centrals_detailed(
            ax, df, dates, result["centrals"], index_map, merged_index_map
        )

        # 标记背驰信号
        self._plot_divergences(ax, df, dates, divergences, index_map, merged_index_map)

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
        dates,
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

            # 确保索引在有效范围内
            valid_top_indices = [idx for idx in top_indices if 0 <= idx < len(dates)]
            ax.scatter(
                [dates[idx] for idx in valid_top_indices],
                [top_prices[i] for i, idx in enumerate(top_indices) if 0 <= idx < len(dates)],
                color=self.colors["top_fractal"],
                marker="v",
                s=120,
                label="顶分型",
                zorder=5,
                edgecolors="black",
            )

            # 添加价格标签和编号
            for idx, price, number in zip(top_indices, top_prices, top_numbers):
                # 确保索引在有效范围内
                if 0 <= idx < len(dates):
                    # 价格标签
                    ax.annotate(
                        f"{price:.2f}",
                        (dates.iloc[idx], price),
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
                        (dates.iloc[idx], price),
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

            # 确保索引在有效范围内
            valid_bottom_indices = [idx for idx in bottom_indices if 0 <= idx < len(dates)]
            ax.scatter(
                [dates[idx] for idx in valid_bottom_indices],
                [bottom_prices[i] for i, idx in enumerate(bottom_indices) if 0 <= idx < len(dates)],
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
                # 确保索引在有效范围内
                if 0 <= idx < len(dates):
                    # 价格标签
                    ax.annotate(
                        f"{price:.2f}",
                        (dates.iloc[idx], price),
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
                        (dates.iloc[idx], price),
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
        dates,
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
                [dates[start_idx], dates[end_idx]],
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
                [dates[start_idx], dates[end_idx]],
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
            # 确保索引在有效范围内
            if 0 <= start_idx < len(dates):
                if stroke.direction == 1:  # 上升笔
                    ax.annotate(
                        f"[{start_number},{end_number}]",
                        (dates.iloc[start_idx], start_price),
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
                        (dates.iloc[start_idx], start_price),
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
        dates,
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
                [dates[start_idx], dates[end_idx]],
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
                [dates[start_idx], dates[end_idx]],
                [start_price, end_price],
                color=color,
                s=15,
                alpha=0.8,
                zorder=15,
            )

            # 添加线段的标签 - 使用 [起始分形编号,结束分形编号] 格式标注
            mid_date = dates.iloc[(start_idx + end_idx) // 2]
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
                (mid_date, mid_price),
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
        self, ax, df, dates, centrals, index_map=None, merged_index_map=None
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

            # 确保索引在有效范围内
            if 0 <= start_idx < len(dates) and 0 <= end_idx < len(dates):
                # 绘制中枢矩形
                start_date = mdates.date2num(dates[start_idx])
                end_date = mdates.date2num(dates[end_idx])
                width = end_date - start_date
                height = high_price - low_price
                rect = Rectangle(
                    (start_date, low_price),
                    width,
                    height,
                    facecolor=self.colors["central_fill"],
                    alpha=0.4,
                    edgecolor=color,
                    linewidth=2,
                    linestyle="--",
                )
                ax.add_patch(rect)
            # 如果索引无效，则跳过这个中枢

            # 添加中枢详细信息
            if 0 <= start_idx < len(dates) and 0 <= end_idx < len(dates):
                mid_idx = start_idx + (end_idx - start_idx) // 2
                if 0 <= mid_idx < len(dates):
                    mid_date = dates.iloc[mid_idx]
                    mid_price = (high_price + low_price) / 2
                else:
                    continue
            else:
                continue

            info_text = (
                f"中枢{i+1}\n{low_price:.2f}-{high_price:.2f}\n区间:{height:.2f}"
            )

            ax.text(
                mid_date,
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
        self, ax, df, dates, x_dates, macd_result, divergences, index_map, merged_index_map=None
    ):
        """绘制MACD指标图"""
        # 获取MACD数据
        macd_line = macd_result["macd_line"]
        signal_line = macd_result["signal_line"]
        histogram = macd_result["histogram"]

        # 绘制MACD线
        ax.plot(x_dates, macd_line, label="MACD", color="blue", linewidth=1.5)
        ax.plot(
            x_dates, signal_line, label="Signal", color="red", linewidth=1.5
        )

        # 绘制柱状图
        colors = ["red" if h >= 0 else "green" for h in histogram]
        ax.bar(x_dates, histogram, color=colors, alpha=0.6, width=0.8)

        for div in divergences:
            # 转换索引以匹配绘图位置
            idx = div["price_index"]

            # 应用合并索引映射
            if merged_index_map:
                idx = merged_index_map.get(idx, idx)

            # 应用索引映射
            if index_map:
                idx = index_map.get(idx, idx)

            # 确保索引在有效范围内
            if idx < 0 or idx >= len(x_dates):
                continue

            ax.axvline(x=x_dates[idx], color="orange", linestyle="--", alpha=0.7, linewidth=1)
            # 转换索引以匹配绘图位置
            macd_idx = div["price_index"]

            # 应用合并索引映射
            if merged_index_map:
                macd_idx = merged_index_map.get(macd_idx, macd_idx)

            # 应用索引映射
            if index_map:
                macd_idx = index_map.get(macd_idx, macd_idx)

            # 确保MACD索引在有效范围内
            if macd_idx < 0 or macd_idx >= len(macd_line):
                macd_value = macd_line.iloc[-1] if len(macd_line) > 0 else 0
            else:
                macd_value = macd_line.iloc[macd_idx]
                
            ax.annotate(
                div["type"],
                (x_dates[idx], macd_value),
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

    def _plot_divergences(self, ax, df, dates, divergences, index_map, merged_index_map=None):
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

            # 确保索引在有效范围内
            if idx < 0 or idx >= len(dates):
                continue

            price = div["price"]
            div_type = div["type"]

            # 背驰标记 - 使用matplotlib支持的箭头标记
            marker = "v" if "顶背驰" in div_type else "^"  # 使用v和^代替↓和↑
            color = "red" if "顶背驰" in div_type else "green"

            ax.scatter(dates.iloc[idx], price, color=color, marker=marker, s=200, zorder=6)
            ax.annotate(
                f"{div_type}\n{price:.2f}",
                (dates.iloc[idx], price),
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
        import traceback
        traceback.print_exc()
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
