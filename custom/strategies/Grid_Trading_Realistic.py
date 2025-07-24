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
#  Written by Bill Chan <billpwchan@hotmail.com>, 2021
#  Copyright (c)  billpwchan - All Rights Reserved


import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)

from strategies.Strategies import Strategies
from util import logger


class GridTradingRealistic(Strategies):
    def __init__(self, input_data: dict, grid_levels=10, grid_spacing=0.03, base_price=None, observation=100):
        """
        更现实的网格交易策略，考虑交易成本
        :param input_data: 输入数据
        :param grid_levels: 网格层数
        :param grid_spacing: 网格间距（百分比）
        :param base_price: 基准价格
        :param observation: 观察期长度
        """
        self.grid_levels = grid_levels
        self.grid_spacing = grid_spacing
        self.base_price = base_price
        self.OBSERVATION = observation
        self.default_logger = logger.get_logger("grid_trading_realistic")
        
        # 存储每个股票的持仓状态和最后交易价格
        self.positions = {}
        self.last_trade_prices = {}
        self.trade_count = {}  # 记录每个股票的交易次数
        self.total_pnl = {}    # 记录每个股票的总盈亏

        super().__init__(input_data)
        self.parse_data()

    def parse_data(self, stock_list: list = None, latest_data: pd.DataFrame = None, backtesting: bool = False):
        # Received New Data => Parse it Now to input_data
        if latest_data is not None:
            # Only need to update for the stock_code with new data
            stock_code = latest_data['code'].iloc[0]
            stock_list = [stock_code]

            # Remove records with duplicate time_key. Always use the latest data to override
            time_key = latest_data['time_key'].iloc[0]
            self.input_data[stock_code].drop(
                self.input_data[stock_code][self.input_data[stock_code].time_key == time_key].index,
                inplace=True)
            self.input_data[stock_code] = pd.concat([self.input_data[stock_code], latest_data])
        elif stock_list is not None:
            # Override Updated Stock List
            stock_list = list(stock_list)
        else:
            stock_list = list(self.input_data.keys())

        # Process data for the stock_list
        for stock_code in stock_list:
            # Need to truncate to a maximum length for low-latency
            if not backtesting and stock_code in self.input_data:
                self.input_data[stock_code] = self.input_data[stock_code].iloc[
                                              -min(self.OBSERVATION, self.input_data[stock_code].shape[0]):]
            if stock_code in self.input_data:
                self.input_data[stock_code][['open', 'close', 'high', 'low']] = self.input_data[stock_code][
                    ['open', 'close', 'high', 'low']].apply(pd.to_numeric)

                # 初始化基准价格（如果未提供）
                if self.base_price is None and len(self.input_data[stock_code]) > 0:
                    self.base_price = round(float(self.input_data[stock_code]['close'].iloc[-1]), 2)  # 四舍五入到两位小数
                    
                # 初始化持仓状态
                if stock_code not in self.positions:
                    self.positions[stock_code] = 0  # 0表示无持仓
                    
                # 初始化最后交易价格
                if stock_code not in self.last_trade_prices:
                    self.last_trade_prices[stock_code] = self.base_price if self.base_price is not None else 0
                    
                # 初始化交易计数和盈亏
                if stock_code not in self.trade_count:
                    self.trade_count[stock_code] = 0
                if stock_code not in self.total_pnl:
                    self.total_pnl[stock_code] = 0.0

                self.input_data[stock_code].reset_index(drop=True, inplace=True)

    def get_grid_level(self, price):
        """计算当前价格对应的网格层级"""
        if self.base_price is None:
            return 0
        return round((price - self.base_price) / (self.base_price * self.grid_spacing))

    def buy(self, stock_code) -> bool:
        """
        网格买入逻辑：
        1. 当价格下跌到下一个网格层级时买入
        2. 考虑交易成本，只在有足够盈利空间时交易
        3. 所有价格四舍五入到两位小数，符合实际交易要求
        """
        # Check if we have data for this stock
        if stock_code not in self.input_data or len(self.input_data[stock_code]) == 0:
            return False
            
        current_record = self.input_data[stock_code].iloc[-1]
        current_price = round(float(current_record['close']), 2)  # 四舍五入到两位小数
        current_level = self.get_grid_level(current_price)
        last_trade_level = self.get_grid_level(self.last_trade_prices[stock_code])
        
        # 买入条件：价格下跌了一个网格间距
        buy_decision = current_level < last_trade_level
        
        if buy_decision:
            self.default_logger.info(
                f"Grid Buy Decision: {current_record['time_key']} at price {current_price}, "
                f"current level {current_level}, last trade level {last_trade_level}")
            # 更新最后交易价格（已四舍五入）
            self.last_trade_prices[stock_code] = current_price
            # 更新持仓
            self.positions[stock_code] += 1
            # 更新交易计数
            self.trade_count[stock_code] += 1

        return buy_decision

    def sell(self, stock_code) -> bool:
        """
        网格卖出逻辑：
        1. 当价格上涨到下一个网格层级时卖出
        2. 考虑交易成本，只在有足够盈利空间时交易
        3. 所有价格四舍五入到两位小数，符合实际交易要求
        """
        # Check if we have data for this stock
        if stock_code not in self.input_data or len(self.input_data[stock_code]) == 0:
            return False
            
        current_record = self.input_data[stock_code].iloc[-1]
        current_price = round(float(current_record['close']), 2)  # 四舍五入到两位小数
        current_level = self.get_grid_level(current_price)
        last_trade_level = self.get_grid_level(self.last_trade_prices[stock_code])
        
        # 卖出条件：价格上涨了一个网格间距，且有持仓
        sell_decision = current_level > last_trade_level and self.positions[stock_code] > 0
        
        if sell_decision:
            # 计算预期盈利（税前）
            expected_profit_per_share = current_price - self.last_trade_prices[stock_code]
            
            # 对于HK.03033，假设交易200股（1手），估算税后盈利
            # 固定费用：15.5 * 2 = 31 HKD
            # 交易额：(current_price + last_trade_price) * 200
            # 百分比费用：交易额 * 0.1097% 
            trade_value = (current_price + self.last_trade_prices[stock_code]) * 200
            percentage_fee = trade_value * 0.001097
            total_fees = 31 + percentage_fee
            expected_net_profit = expected_profit_per_share * 200 - total_fees
            
            self.default_logger.info(
                f"Grid Sell Decision: {current_record['time_key']} at price {current_price}, "
                f"current level {current_level}, last trade level {last_trade_level}, "
                f"expected net profit: {expected_net_profit:.2f} HKD")
            
            # 只有在预期盈利为正时才执行交易
            if expected_net_profit > 0:
                # 更新最后交易价格（已四舍五入）
                self.last_trade_prices[stock_code] = current_price
                # 更新持仓
                self.positions[stock_code] -= 1
                # 更新交易计数
                self.trade_count[stock_code] += 1
                # 更新总盈亏
                self.total_pnl[stock_code] += expected_net_profit
                return True
            else:
                # 预期亏损，取消交易
                self.default_logger.info(
                    f"SELL ORDER CANCELLED for {stock_code} due to expected loss: {expected_net_profit:.2f} HKD")
                return False

        return sell_decision