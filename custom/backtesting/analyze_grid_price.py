#!/usr/bin/env python3
"""
HK.03033网格基准价格分析脚本
基于最近100天价格数据重新确定网格基准价格
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_grid_base_price():
    """分析HK.03033的网格基准价格"""
    
    # 获取HK.03033（南方恒生科技ETF）的历史数据
    ticker = '3033.HK'
    stock = yf.Ticker(ticker)
    
    # 获取最近100天的日线数据
    hist = stock.history(period='100d')
    
    if hist.empty:
        print("无法获取数据")
        return
    
    # 计算关键价格指标
    current_price = hist['Close'].iloc[-1]
    avg_100d = hist['Close'].mean()
    min_100d = hist['Close'].min()
    max_100d = hist['Close'].max()
    
    # 计算价格波动范围
    price_range = max_100d - min_100d
    volatility = hist['Close'].std()
    
    print("=" * 50)
    print("HK.03033 网格基准价格分析报告")
    print("=" * 50)
    print(f"当前价格：{current_price:.3f} HKD")
    print(f"100天均价：{avg_100d:.3f} HKD")
    print(f"100天最低价：{min_100d:.3f} HKD")
    print(f"100天最高价：{max_100d:.3f} HKD")
    print(f"价格波动区间：{price_range:.3f} HKD")
    print(f"价格标准差：{volatility:.3f} HKD")
    print(f"波动率：{(volatility/avg_100d)*100:.2f}%")
    
    # 网格基准价格建议
    print("\n" + "=" * 50)
    print("网格基准价格建议")
    print("=" * 50)
    
    # 方案1：基于当前价格
    base_price_current = round(current_price, 3)
    print(f"方案1 - 当前价格基准：{base_price_current} HKD")
    
    # 方案2：基于100天均价
    base_price_avg = round(avg_100d, 3)
    print(f"方案2 - 100天均价基准：{base_price_avg} HKD")
    
    # 方案3：基于价格区间中值
    base_price_mid = round((max_100d + min_100d) / 2, 3)
    print(f"方案3 - 价格区间中值：{base_price_mid} HKD")
    
    # 方案4：加权平均（当前价格权重60%，历史均价权重40%）
    base_price_weighted = round(current_price * 0.6 + avg_100d * 0.4, 3)
    print(f"方案4 - 加权平均价格：{base_price_weighted} HKD")
    
    # 推荐方案
    print("\n" + "=" * 50)
    print("推荐方案")
    print("=" * 50)
    
    # 基于当前价格趋势判断
    recent_trend = "上涨" if current_price > avg_100d else "下跌"
    trend_strength = abs(current_price - avg_100d) / avg_100d
    
    if trend_strength < 0.02:  # 趋势较弱，价格接近均价
        recommended_price = base_price_weighted
        reason = "价格接近长期均价，市场相对平衡"
    elif current_price > avg_100d:  # 上涨趋势
        if trend_strength < 0.05:  # 温和上涨
            recommended_price = base_price_current
            reason = "温和上涨趋势，以当前价格为基准"
        else:  # 强势上涨
            recommended_price = base_price_avg
            reason = "强势上涨后可能有回调，以均价为基准更稳健"
    else:  # 下跌趋势
        if trend_strength < 0.05:  # 温和下跌
            recommended_price = base_price_current
            reason = "温和下跌趋势，以当前价格为基准"
        else:  # 强势下跌
            recommended_price = base_price_weighted
            reason = "强势下跌后可能反弹，加权平均更平衡"
    
    print(f"推荐网格基准价格：{recommended_price} HKD")
    print(f"推荐理由：{reason}")
    
    # 网格参数计算
    print("\n" + "=" * 50)
    print("网格参数计算（基于推荐价格）")
    print("=" * 50)
    
    # 使用3%网格间距（与当前策略一致）
    grid_spacing = 0.03
    
    # 计算网格边界
    upper_bound = recommended_price * (1 + 5 * grid_spacing)  # 向上5个网格
    lower_bound = recommended_price * (1 - 5 * grid_spacing)   # 向下5个网格
    
    print(f"网格间距：{grid_spacing*100}%")
    print(f"网格上限：{upper_bound:.3f} HKD")
    print(f"网格下限：{lower_bound:.3f} HKD")
    print(f"网格区间：{lower_bound:.3f} - {upper_bound:.3f} HKD")
    
    # 验证网格区间是否覆盖历史价格
    if min_100d >= lower_bound and max_100d <= upper_bound:
        coverage = "完全覆盖"
    elif min_100d < lower_bound or max_100d > upper_bound:
        coverage = "部分覆盖"
    else:
        coverage = "未覆盖"
    
    print(f"历史价格覆盖情况：{coverage}")
    
    # 建议调整
    print("\n" + "=" * 50)
    print("策略优化建议")
    print("=" * 50)
    
    if coverage == "部分覆盖":
        print("1. 建议扩大网格范围以覆盖历史价格区间")
        print(f"2. 可考虑调整网格间距至 {(max_100d-min_100d)/(recommended_price*10):.1%}")
    
    print("3. 提高资金利用率：")
    print("   - 增加MaxPercPerAsset至50-80%")
    print("   - 增加网格数量至15-20个")
    print("   - 考虑使用2%网格间距提高交易频率")
    
    return {
        'recommended_base_price': recommended_price,
        'current_price': current_price,
        'avg_100d': avg_100d,
        'min_100d': min_100d,
        'max_100d': max_100d,
        'volatility': volatility
    }

if __name__ == "__main__":
    analyze_grid_base_price()