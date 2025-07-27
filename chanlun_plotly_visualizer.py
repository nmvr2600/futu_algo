#!/usr/bin/env python3
"""
缠论Plotly可视化工具
使用Plotly库生成交互式缠论分析图表
支持K线图、分型、笔、线段、中枢等元素的可视化
"""

import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from util.chanlun import ChanlunProcessor
from custom.chanlun_selector_demo import get_stock_data


class PlotlyChanlunVisualizer:
    """基于Plotly的缠论可视化器"""
    
    def __init__(self):
        # 颜色配置
        self.colors = {
            "up_stroke": "#1f77b4",      # 蓝色笔
            "down_stroke": "#ff7f0e",    # 橙色笔
            "up_segment": "#ff4757",     # 红色线段
            "down_segment": "#2ed573",   # 绿色线段
            "top_fractal": "#d62728",    # 红色顶分型
            "bottom_fractal": "#2ca02c", # 绿色底分型
            "central": "#9467bd",        # 紫色中枢
            "central_fill": "#e6e6fa",   # 浅紫色中枢填充
            "bullish": "#26a69a",        # 牛市颜色
            "bearish": "#ef5350",        # 熊市颜色
        }
    
    def create_comprehensive_chart(self, df, result, stock_code, save_path=None):
        """
        创建综合缠论分析图表
        
        Args:
            df: 原始K线数据
            result: 缠论分析结果
            stock_code: 股票代码
            save_path: 保存路径（可选）
            
        Returns:
            fig: Plotly图表对象
        """
        # 创建子图布局 - 主图和MACD副图
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # 绘制K线图
        self._plot_candlestick(fig, df, row=1, col=1)
        
        # 绘制缠论元素
        self._plot_fractals(fig, df, result, row=1, col=1)
        self._plot_strokes(fig, df, result, row=1, col=1)
        self._plot_segments(fig, df, result, row=1, col=1)
        self._plot_centrals(fig, df, result, row=1, col=1)
        
        # 绘制MACD指标
        self._plot_macd(fig, df, result, row=2, col=1)
        
        # 设置图表标题
        title_text = (
            f"{stock_code} - 缠论分析<br>"
            f'分形:{len(result["fractals"])} | '
            f'笔:{len(result["strokes"])} | '
            f'中枢:{len(result["centrals"])}'
        )
        
        fig.update_layout(
            title=title_text,
            title_font_size=16,
            height=800,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        # 设置坐标轴标签
        fig.update_xaxes(title_text="时间", row=2, col=1)
        fig.update_yaxes(title_text="价格", row=1, col=1)
        fig.update_yaxes(title_text="MACD", row=2, col=1)
        
        # 保存图表
        if save_path:
            fig.write_html(save_path)
            print(f"图表已保存到: {save_path}")
        
        return fig
    
    def _plot_candlestick(self, fig, df, row, col):
        """绘制K线图"""
        fig.add_trace(
            go.Candlestick(
                x=df['time_key'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="K线",
                increasing_line_color='red',
                decreasing_line_color='green',
                increasing_fillcolor='red',
                decreasing_fillcolor='green'
            ),
            row=row, col=col
        )
    
    def _plot_fractals(self, fig, df, result, row, col):
        """绘制分型"""
        fractals = result.get("fractals", [])
        if not fractals:
            return
        
        # 提取顶分型和底分型数据
        top_fractals = [f for f in fractals if f.type.value == "top"]
        bottom_fractals = [f for f in fractals if f.type.value == "bottom"]
        
        # 绘制顶分型
        if top_fractals:
            top_time_keys = [f.time_key for f in top_fractals]
            top_prices = [f.price for f in top_fractals]
            top_numbers = [str(f.idx) for f in top_fractals]  # 分型编号
            
            # 绘制顶分型标记和编号
            fig.add_trace(
                go.Scatter(
                    x=top_time_keys,
                    y=top_prices,
                    mode='markers+text',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color=self.colors["top_fractal"],
                        line=dict(width=1, color='black')
                    ),
                    text=top_numbers,
                    textposition="top center",
                    textfont=dict(
                        size=11,
                        color='white',
                        family='Arial Black'
                    ),
                    name="顶分型",
                    hovertemplate='<b>顶分型 #%{text}</b><br>价格: %{y:.2f}<extra></extra>',
                    showlegend=False
                ),
                row=row, col=col
            )
        
        # 绘制底分型
        if bottom_fractals:
            bottom_time_keys = [f.time_key for f in bottom_fractals]
            bottom_prices = [f.price for f in bottom_fractals]
            bottom_numbers = [str(f.idx) for f in bottom_fractals]  # 分型编号
            
            # 绘制底分型标记和编号
            fig.add_trace(
                go.Scatter(
                    x=bottom_time_keys,
                    y=bottom_prices,
                    mode='markers+text',
                    marker=dict(
                        symbol='triangle-up',
                        size=12,
                        color=self.colors["bottom_fractal"],
                        line=dict(width=1, color='black')
                    ),
                    text=bottom_numbers,
                    textposition="bottom center",
                    textfont=dict(
                        size=11,
                        color='white',
                        family='Arial Black'
                    ),
                    name="底分型",
                    hovertemplate='<b>底分型 #%{text}</b><br>价格: %{y:.2f}<extra></extra>',
                    showlegend=False
                ),
                row=row, col=col
            )
    
    def _plot_strokes(self, fig, df, result, row, col):
        """绘制笔"""
        strokes = result.get("strokes", [])
        if not strokes:
            return
        
        for i, stroke in enumerate(strokes):
            # 检查time_key是否存在
            if stroke.start_time_key is None or stroke.end_time_key is None:
                continue
                
            start_time = stroke.start_time_key
            end_time = stroke.end_time_key
            start_price = stroke.start_price
            end_price = stroke.end_price
            
            color = self.colors["up_stroke"] if stroke.direction == 1 else self.colors["down_stroke"]
            
            fig.add_trace(
                go.Scatter(
                    x=[start_time, end_time],
                    y=[start_price, end_price],
                    mode='lines+markers',
                    line=dict(color=color, width=2, dash="dash"),  # 笔较细，虚线
                    marker=dict(size=6, color=color, symbol="circle"),  # 圆形标记
                    name=f"笔 {stroke.idx}",
                    hovertemplate=f'<b>笔 {stroke.idx}</b><br>方向: {"上涨" if stroke.direction == 1 else "下跌"}<br>价格: %{{y:.2f}}<extra></extra>',
                    showlegend=False
                ),
                row=row, col=col
            )
    
    def _plot_segments(self, fig, df, result, row, col):
        """绘制线段"""
        segments = result.get("segments", [])
        if not segments:
            return
        
        for i, segment in enumerate(segments):
            # 检查time_key是否存在
            if segment.start_time_key is None or segment.end_time_key is None:
                continue
                
            start_time = segment.start_time_key
            end_time = segment.end_time_key
            start_price = segment.start_price
            end_price = segment.end_price
            
            color = self.colors["up_segment"] if segment.direction == 1 else self.colors["down_segment"]
            
            fig.add_trace(
                go.Scatter(
                    x=[start_time, end_time],
                    y=[start_price, end_price],
                    mode='lines+markers',
                    line=dict(color=color, width=4, dash="solid"),  # 线段更粗，实线
                    marker=dict(size=8, color=color, symbol="diamond"),  # 菱形标记
                    name=f"线段 {segment.idx}",
                    hovertemplate=f'<b>线段 {segment.idx}</b><br>方向: {"上涨" if segment.direction == 1 else "下跌"}<br>价格: %{{y:.2f}}<extra></extra>',
                    showlegend=False
                ),
                row=row, col=col
            )
    
    def _plot_centrals(self, fig, df, result, row, col):
        """绘制中枢"""
        centrals = result.get("centrals", [])
        if not centrals:
            return
        
        for i, central in enumerate(centrals):
            # 检查time_key是否存在
            if central.start_time_key is None or central.end_time_key is None:
                continue
                
            start_time = central.start_time_key
            end_time = central.end_time_key
            
            # 计算中点时间
            # 由于我们只有起始和结束时间，我们可以取它们的中点
            # 在实际应用中，可能需要更精确的计算方法
            mid_time = start_time + (end_time - start_time) / 2
            
            # 绘制中枢区域
            fig.add_shape(
                type="rect",
                x0=start_time,
                x1=end_time,
                y0=central.low,
                y1=central.high,
                line=dict(color=self.colors["central"], width=2, dash="dot"),
                fillcolor=self.colors["central_fill"],
                opacity=0.3,
                layer="below",
                row=row, col=col
            )
            
            # 添加中枢标签
            mid_price = (central.high + central.low) / 2
            
            fig.add_annotation(
                x=mid_time,
                y=mid_price,
                text=f"中枢{i+1}",
                showarrow=False,
                bgcolor=self.colors["central"],
                font=dict(color="white", size=10),
                row=row, col=col
            )
    
    def _plot_macd(self, fig, df, result, row, col):
        """绘制MACD指标"""
        # 计算MACD
        close = df["close"]
        ema_fast = close.ewm(span=12, adjust=False).mean()
        ema_slow = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        # 绘制MACD线
        fig.add_trace(
            go.Scatter(
                x=df['time_key'],
                y=macd_line,
                mode='lines',
                line=dict(color='blue', width=1.5),
                name='MACD'
            ),
            row=row, col=col
        )
        
        # 绘制信号线
        fig.add_trace(
            go.Scatter(
                x=df['time_key'],
                y=signal_line,
                mode='lines',
                line=dict(color='red', width=1.5),
                name='Signal'
            ),
            row=row, col=col
        )
        
        # 绘制柱状图
        colors = ['red' if h >= 0 else 'green' for h in histogram]
        fig.add_trace(
            go.Bar(
                x=df['time_key'],
                y=histogram,
                marker_color=colors,
                opacity=0.6,
                name='Histogram'
            ),
            row=row, col=col
        )


def generate_plotly_chart(
    stock_code,
    period="2y",
    interval="1d",
    kline_count=None,
    save_dir="./chanlun_reports",
):
    """
    生成Plotly缠论分析图表
    
    Args:
        stock_code: 股票代码
        period: 时间段 ('1y', '2y', '6mo', etc.)
        interval: 时间间隔 ('1d', '1wk', etc.)
        kline_count: 指定使用的K线数量
        save_dir: 保存目录
    """
    print(f"正在生成 {stock_code} 的Plotly缠论分析图表...")
    print(f"参数: period={period}, interval={interval}, kline_count={kline_count}")
    
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
        
        # 检查处理结果
        if not result or not isinstance(result, dict):
            print("缠论分析返回无效结果")
            return None
        
        # 检查关键数据是否存在
        required_keys = ['fractals', 'strokes', 'centrals']
        for key in required_keys:
            if key not in result or result[key] is None:
                result[key] = []
        
        # 创建可视化器
        visualizer = PlotlyChanlunVisualizer()
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存图表
        chart_path = os.path.join(save_dir, f"{stock_code}_{timestamp}_plotly.html")
        fig = visualizer.create_comprehensive_chart(data, result, stock_code, chart_path)
        
        print(f"\n=== {stock_code} Plotly图表生成完成 ===")
        print(f"图表: {chart_path}")
        print(
            f"分形: {len(result['fractals'])} | 笔: {len(result['strokes'])} | 中枢: {len(result['centrals'])}"
        )
        
        return chart_path
        
    except Exception as e:
        print(f"生成Plotly图表失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数 - 处理命令行参数并生成Plotly图表"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='缠论Plotly图表生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s 0700.HK                    # 生成腾讯图表，使用默认参数
  %(prog)s 0700.HK -p 1y              # 生成1年数据图表
  %(prog)s 0700.HK -k 500             # 使用最近500根K线
  %(prog)s 0700.HK -p 6mo -k 360      # 生成6个月图表，限制360根K线
  %(prog)s 0700.HK -p 1mo -k 100 -i 15m  # 生成1个月图表，100根15分钟K线
        """
    )
    
    # 添加参数
    parser.add_argument(
        'stock_code',
        help='股票代码 (如: 0700.HK, 0005.HK, AAPL)'
    )
    
    parser.add_argument(
        '-p', '--period',
        default='2y',
        choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        help='数据周期 (默认: 2y)'
    )
    
    parser.add_argument(
        '-k', '--kline_count',
        type=int,
        help='使用K线数量 (如: 360, 500, 720)'
    )
    
    parser.add_argument(
        '-i', '--interval',
        default='1d',
        choices=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
        help='K线周期 (默认: 1d)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./chanlun_reports',
        help='输出目录 (默认: ./chanlun_reports)'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 生成图表
    try:
        fig = generate_plotly_chart(
            stock_code=args.stock_code,
            period=args.period,
            interval=args.interval,
            kline_count=args.kline_count,
            save_dir=args.output
        )
        
        if fig:
            print(f"✅ Plotly图表生成成功!")
        else:
            print(f"❌ Plotly图表生成失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 使用命令行参数
        exit(main())
    else:
        # 默认处理腾讯股票
        generate_plotly_chart("0700.HK")