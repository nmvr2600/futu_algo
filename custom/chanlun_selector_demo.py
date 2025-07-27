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

from custom.filters.Chanlun_Filter import ChanlunFilter
from engines.stock_filter_engine import StockFilter
from util.chanlun import ChanlunProcessor


def get_stock_data(symbol, period="1y", interval="1d"):
    """
    获取单个股票的数据并确保列名正确
    :param symbol: 股票代码
    :param period: 数据周期 ("1y", "2y", "5y", "10y", "ytd", "max")
    :param interval: 数据间隔 ("1d", "1wk", "1mo", "5m", "15m", "30m", "1h")
    """
    try:
        # 使用yfinance获取指定周期和间隔的数据
        ticker = yf.Ticker(symbol)
        # 添加超时处理，防止API调用卡死
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("获取股票数据超时")
        
        # 设置5秒超时
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            data = ticker.history(period=period, interval=interval)
        finally:
            signal.alarm(0)  # 取消超时
        
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
            # 确保有time_key列，直接使用索引（已经是datetime类型）
            data['time_key'] = data.index
        return data
    except TimeoutError:
        print(f"获取{symbol}数据超时")
        return pd.DataFrame()
    except Exception as e:
        print(f"获取{symbol}数据时出错: {e}")
        return pd.DataFrame()


def analyze_stock_at_level(symbol, level_name, period, interval):
    """
    在指定级别分析股票
    :param symbol: 股票代码
    :param level_name: 级别名称
    :param period: 数据周期
    :param interval: 数据间隔
    """
    print(f"\n分析 {symbol} 的 {level_name} 级别数据...")
    
    data = get_stock_data(symbol, period=period, interval=interval)
    if data.empty:
        print(f"无法获取 {symbol} 的 {level_name} 级别数据")
        return None
        
    print(f"{level_name} 级别数据形状: {data.shape}")
    
    # 处理缠论结构
    processor = ChanlunProcessor()
    try:
        result = processor.process(data)
        print(f"{level_name} 级别缠论分析结果:")
        print(f"  分型数量: {len(result['fractals'])}")
        print(f"  笔数量: {len(result['strokes'])}")
        print(f"  线段数量: {len(result['segments'])}")
        print(f"  中枢数量: {len(result['centrals'])}")
        return result
    except Exception as e:
        print(f"{level_name} 级别缠论处理出错: {e}")
        return None


def run_chanlun_selection(stock_list: list, buy_point_type: int = 1, 
                         main_period: str = "1y", main_interval: str = "1d",
                         sub_period: str = "1mo", sub_interval: str = "30m"):
    """
    运行缠论选股器
    :param stock_list: 股票列表
    :param buy_point_type: 买点类型 (1: 第一类买点, 2: 第二类买点, 3: 第三类买点)
    :param main_period: 主级别数据周期
    :param main_interval: 主级别数据间隔
    :param sub_period: 次级别数据周期
    :param sub_interval: 次级别数据间隔
    :return: 符合条件的股票列表
    """
    # 创建缠论筛选器，指定主次级别参数
    chanlun_filter = ChanlunFilter(
        buy_point_type=buy_point_type,
        main_level=main_interval,
        sub_level=sub_interval
    )
    
    # 创建股票筛选器
    stock_filter = StockFilter([chanlun_filter], stock_list)
    
    # 获取符合条件的股票
    selected_stocks = stock_filter.get_filtered_equity_pools()
    
    # 显示筛选过程中的详细信息
    print(f"筛选条件: 买点类型 {buy_point_type}, 主级别 {main_interval}, 次级别 {sub_interval}")
    print(f"筛选结果: 共找到 {len(selected_stocks)} 只符合条件的股票")
    
    return selected_stocks


def detailed_analysis():
    """
    对单个股票进行详细的多级别分析
    """
    symbol = "0700.HK"  # 腾讯
    
    # 日线级别分析
    analyze_stock_at_level(symbol, "日线", "1y", "1d")
    
    # 周线级别分析
    analyze_stock_at_level(symbol, "周线", "5y", "1wk")
    
    # 30分钟级别分析
    analyze_stock_at_level(symbol, "30分钟", "1mo", "30m")


if __name__ == "__main__":
    print("缠论选股器 - 支持指定时间级别的分析")
    print("="*50)
    
    # 进行详细分析
    detailed_analysis()
    
    # 使用港股列表进行测试
    hk_stocks = ["0700.HK", "0941.HK", "0005.HK", "1299.HK", "0883.HK"]  # 腾讯、中国移动、汇丰、友邦、中海油
    
    print("\n" + "="*50)
    print("使用港股进行缠论选股测试")
    
    # 测试所有三种买点类型
    for buy_point_type in [1, 2, 3]:
        print(f"\n{buy_point_type}. 日线级别第{buy_point_type}类买点筛选:")
        result = run_chanlun_selection(
            hk_stocks, 
            buy_point_type=buy_point_type,
            main_period="1y",
            main_interval="1d",
            sub_period="1mo",
            sub_interval="30m"
        )
        
        print("符合条件的股票:")
        for stock in result:
            print(f"- {stock}")
        
        if not result:
            print("- 无符合条件的股票")
        
    # 额外测试：尝试找到更多满足条件的股票
    print("\n" + "="*50)
    print("扩展测试：寻找更多可能的候选股票")
    
    # 增加更多的港股股票进行测试
    extended_hk_stocks = ["0700.HK", "0941.HK", "0005.HK", "1299.HK", "0883.HK", 
                         "0016.HK", "0011.HK", "0001.HK", "0066.HK", "0857.HK"]
    
    for buy_point_type in [1, 2, 3]:
        print(f"\n扩展测试 {buy_point_type}. 日线级别第{buy_point_type}类买点筛选:")
        result = run_chanlun_selection(
            extended_hk_stocks, 
            buy_point_type=buy_point_type,
            main_period="1y",
            main_interval="1d",
            sub_period="1mo",
            sub_interval="30m"
        )
        
        print("符合条件的股票:")
        for stock in result:
            print(f"- {stock}")
        
        if not result:
            print("- 无符合条件的股票")