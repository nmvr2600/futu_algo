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

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def get_stock_data(symbol, period="1d", interval="1m"):
    """
    获取单个股票的数据并确保列名正确
    :param symbol: 股票代码
    :param period: 数据周期 ("1d", "5d", "1mo", "3mo")
    :param interval: 数据间隔 ("1m", "2m", "5m", "15m", "30m", "1h")
    Note: yfinance has limitations on 1m data - only 7 days of data with 1m interval
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
            data['time_key'] = data.index.strftime('%Y-%m-%d %H:%M:%S')
        return data
    except Exception as e:
        print(f"获取{symbol}数据时出错: {e}")
        return pd.DataFrame()


def analyze_stock_1min_level(symbol):
    """
    在1分钟级别分析股票
    :param symbol: 股票代码
    """
    print(f"分析 {symbol} 的 1分钟 级别数据...")
    
    # 获取1分钟级别的数据（最近1天）
    data = get_stock_data(symbol, period="1d", interval="1m")
    if data.empty:
        print(f"无法获取 {symbol} 的 1分钟 级别数据")
        return None
        
    print(f"1分钟 级别数据形状: {data.shape}")
    print("数据前5行:")
    print(data.head())
    print("\n数据后5行:")
    print(data.tail())
    
    # 处理缠论结构
    processor = ChanlunProcessor()
    try:
        result = processor.process(data)
        print(f"\n1分钟 级别缠论分析结果:")
        print(f"  分型数量: {len(result['fractals'])}")
        print(f"  笔数量: {len(result['strokes'])}")
        print(f"  线段数量: {len(result['segments'])}")
        print(f"  中枢数量: {len(result['centrals'])}")
        
        # 显示分型信息
        if result['fractals']:
            print(f"\n最近的5个分型:")
            for fractal in result['fractals'][-5:]:
                print(f"  时间: {fractal.timestamp}, 类型: {fractal.type.value}, 价格: {fractal.price}")
        
        # 显示笔信息
        if result['strokes']:
            print(f"\n最近的3笔:")
            for stroke in result['strokes'][-3:]:
                direction = "上涨" if stroke.direction == 1 else "下跌"
                print(f"  从 {stroke.start_timestamp} 到 {stroke.end_timestamp}, {direction}, 价格从 {stroke.start_price} 到 {stroke.end_price}")
        
        # 显示线段信息
        if result['segments']:
            print(f"\n最近的2个线段:")
            for segment in result['segments'][-2:]:
                direction = "上涨" if segment.direction == 1 else "下跌"
                print(f"  从 {segment.start_timestamp} 到 {segment.end_timestamp}, {direction}, 价格从 {segment.start_price} 到 {segment.end_price}")
        
        # 显示中枢信息
        if result['centrals']:
            print(f"\n中枢信息:")
            for central in result['centrals']:
                print(f"  从 {central.start_timestamp} 到 {central.end_timestamp}, 价格区间: {central.low} - {central.high}")
        else:
            print(f"\n未发现中枢")
            
        return result
    except Exception as e:
        print(f"1分钟 级别缠论处理出错: {e}")
        return None


if __name__ == "__main__":
    print("腾讯(0700.HK) 1分钟级别缠论分析")
    print("="*50)
    
    # 分析腾讯在1分钟级别的数据
    result = analyze_stock_1min_level("0700.HK")