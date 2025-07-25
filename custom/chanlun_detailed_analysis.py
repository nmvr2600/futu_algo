#  Futu Algo: Algorithmic High-Frequency Trading Framework
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Written by Claude Chan <claude@example.com>, 2025
#  Copyright (c)  billpwchan - All Rights Reserved

import sys
import os
import pandas as pd
import yfinance as yf
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def get_stock_data(symbol, period="2y", interval="1d"):
    """
    获取单个股票的数据并确保列名正确
    :param symbol: 股票代码
    :param period: 数据周期 ("1y", "2y", "5y", "10y", "ytd", "max")
    :param interval: 数据间隔 ("1d", "1wk", "1mo")
    """
    try:
        # 使用yfinance获取指定周期和间隔的数据
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        # 确保列名正确
        if not data.empty:
            # 重命名列以匹配缠论处理器的期望
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            # 确保有time_key列
            data['time_key'] = data.index.strftime('%Y-%m-%d')
        return data
    except Exception as e:
        print(f"获取{symbol}数据时出错: {e}")
        return pd.DataFrame()


def detailed_stroke_analysis(strokes):
    """
    详细分析笔序列
    """
    print("\n详细笔序列分析:")
    print("="*50)
    
    if len(strokes) < 3:
        print("笔数不足3笔，无法形成中枢")
        return
    
    # 显示所有笔的信息
    for i, stroke in enumerate(strokes):
        direction = "上涨" if stroke.direction == 1 else "下跌"
        print(f"笔 {i+1:2d}: {direction:4s} 从 {stroke.start_price:8.2f} 到 {stroke.end_price:8.2f} ({stroke.start_timestamp} -> {stroke.end_timestamp})")
    
    # 检查所有连续的三笔组合
    print("\n检查所有连续三笔组合:")
    print("-"*50)
    
    found_valid_central = False
    for i in range(len(strokes) - 2):
        stroke1 = strokes[i]
        stroke2 = strokes[i+1]
        stroke3 = strokes[i+2]
        
        # 检查是否符合中枢形成模式
        is_valid_pattern = ((stroke1.direction == 1 and stroke2.direction == -1 and stroke3.direction == 1) or
                            (stroke1.direction == -1 and stroke2.direction == 1 and stroke3.direction == -1))
        
        if is_valid_pattern:
            # 计算中枢区间
            if stroke1.direction == 1:  # 上涨->下跌->上涨
                central_high = min(stroke1.end_price, stroke3.start_price)
                central_low = max(stroke2.start_price, stroke2.end_price)
            else:  # 下跌->上涨->下跌
                central_high = min(stroke2.start_price, stroke2.end_price)
                central_low = max(stroke1.end_price, stroke3.start_price)
                
            is_valid_central = central_high > central_low
            
            pattern_type = "上涨->下跌->上涨" if stroke1.direction == 1 else "下跌->上涨->下跌"
            print(f"组合 {i+1:2d}-{i+3:2d}: {pattern_type} 模式")
            print(f"  笔{i+1:2d}: {'上涨' if stroke1.direction == 1 else '下跌'} {stroke1.start_price:8.2f} -> {stroke1.end_price:8.2f}")
            print(f"  笔{i+2:2d}: {'上涨' if stroke2.direction == 1 else '下跌'} {stroke2.start_price:8.2f} -> {stroke2.end_price:8.2f}")
            print(f"  笔{i+3:2d}: {'上涨' if stroke3.direction == 1 else '下跌'} {stroke3.start_price:8.2f} -> {stroke3.end_price:8.2f}")
            print(f"  潜在中枢区间: {central_low:8.2f} - {central_high:8.2f}")
            
            if is_valid_central:
                print(f"  *** 有效中枢! ***")
                found_valid_central = True
            else:
                print(f"  无效中枢 (高点不大于低点)")
            print()
    
    if not found_valid_central:
        print("未找到有效的中枢模式")


def analyze_stock_detailed(symbol):
    """
    详细分析股票数据
    :param symbol: 股票代码
    """
    print(f"详细分析 {symbol} 的数据...")
    
    # 获取日线级别的数据（最近2年）
    data = get_stock_data(symbol, period="2y", interval="1d")
    if data.empty:
        print(f"无法获取 {symbol} 的 日线 级别数据")
        return None
        
    print(f"日线 级别数据形状: {data.shape}")
    
    # 处理缠论结构
    processor = ChanlunProcessor()
    try:
        result = processor.process(data)
        print(f"\n日线 级别缠论分析结果:")
        print(f"  分型数量: {len(result['fractals'])}")
        print(f"  笔数量: {len(result['strokes'])}")
        print(f"  线段数量: {len(result['segments'])}")
        print(f"  中枢数量: {len(result['centrals'])}")
        
        # 详细分析笔序列
        detailed_stroke_analysis(result['strokes'])
            
        return result
    except Exception as e:
        print(f"日线 级别缠论处理出错: {e}")
        return None


if __name__ == "__main__":
    print("腾讯(0700.HK) 日线级别缠论分析 - 详细笔序列分析")
    print("="*60)
    
    # 分析腾讯在日线级别的数据
    result = analyze_stock_detailed("0700.HK")