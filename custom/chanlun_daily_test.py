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


def analyze_stock_daily_level(symbol):
    """
    在日线级别分析股票，使用更长时间周期以识别中枢
    :param symbol: 股票代码
    """
    print(f"分析 {symbol} 的 日线 级别数据...")
    
    # 获取日线级别的数据（最近2年）
    data = get_stock_data(symbol, period="2y", interval="1d")
    if data.empty:
        print(f"无法获取 {symbol} 的 日线 级别数据")
        return None
        
    print(f"日线 级别数据形状: {data.shape}")
    print("数据前5行:")
    print(data.head())
    print("\n数据后5行:")
    print(data.tail())
    
    # 处理缠论结构
    processor = ChanlunProcessor()
    try:
        result = processor.process(data)
        print(f"\n日线 级别缠论分析结果:")
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
            print(f"\n所有笔信息（显示前10笔）:")
            for i, stroke in enumerate(result['strokes'][:10]):
                direction = "上涨" if stroke.direction == 1 else "下跌"
                print(f"  笔 {i+1}: 从 {stroke.start_timestamp} 到 {stroke.end_timestamp}, {direction}, 价格从 {stroke.start_price} 到 {stroke.end_price}")
        
        # 显示线段信息
        if result['segments']:
            print(f"\n所有线段:")
            for segment in result['segments']:
                direction = "上涨" if segment.direction == 1 else "下跌"
                print(f"  从 {segment.start_timestamp} 到 {segment.end_timestamp}, {direction}, 价格从 {segment.start_price} 到 {segment.end_price}")
        
        # 显示中枢信息
        if result['centrals']:
            print(f"\n中枢信息:")
            for i, central in enumerate(result['centrals']):
                print(f"  中枢 {i+1}:")
                print(f"    从 {central.start_timestamp} 到 {central.end_timestamp}")
                print(f"    价格区间: {central.low} - {central.high}")
                print(f"    构成笔数: {len(central.strokes)}")
        else:
            print(f"\n未发现中枢")
            # 检查是否有足够的笔来形成中枢
            if len(result['strokes']) >= 3:
                print("  有足够的笔形成中枢，但未识别到有效的中枢模式")
                # 显示前几笔的信息以帮助调试
                print("  前6笔信息:")
                for i, stroke in enumerate(result['strokes'][:6]):
                    direction = "上涨" if stroke.direction == 1 else "下跌"
                    print(f"    笔 {i+1}: {direction}, 价格从 {stroke.start_price} 到 {stroke.end_price}")
            
        return result
    except Exception as e:
        print(f"日线 级别缠论处理出错: {e}")
        return None


if __name__ == "__main__":
    print("腾讯(0700.HK) 日线级别缠论分析（2年数据）")
    print("="*50)
    
    # 分析腾讯在日线级别的数据
    result = analyze_stock_daily_level("0700.HK")