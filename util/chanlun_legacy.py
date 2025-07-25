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

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class FractalType(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    UNKNOWN = "unknown"


@dataclass
class Fractal:
    """分型结构"""

    index: int
    type: FractalType
    price: float
    timestamp: str


@dataclass
class Stroke:
    """笔结构"""

    start_index: int
    end_index: int
    start_price: float
    end_price: float
    direction: int  # 1 for up, -1 for down
    start_timestamp: str
    end_timestamp: str


@dataclass
class Segment:
    """线段结构"""

    start_index: int
    end_index: int
    start_price: float
    end_price: float
    direction: int  # 1 for up, -1 for down
    start_timestamp: str
    end_timestamp: str


@dataclass
class Central:
    """中枢结构"""

    start_index: int
    end_index: int
    high: float
    low: float
    start_timestamp: str
    end_timestamp: str
    strokes: List[Stroke]  # 构成中枢的笔


class ChanlunProcessor:
    """缠论处理器"""

    def __init__(self):
        self.fractals: List[Fractal] = []
        self.strokes: List[Stroke] = []
        self.segments: List[Segment] = []
        self.centrals: List[Central] = []
        self.merged_df: Optional[pd.DataFrame] = None  # 存储合并后的K线数据

    def _merge_k_lines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        合并K线数据，处理包含关系
        :param df: 原始K线数据
        :return: 合并后的K线数据
        """
        # 确保数据按时间排序
        df = df.sort_values("time_key").reset_index(drop=True)

        # 初始化合并后的数据
        merged_data = []
        i = 0

        while i < len(df):
            # 如果是第一根K线，直接添加
            if len(merged_data) == 0:
                merged_data.append(
                    {
                        "time_key": df["time_key"].iloc[i],
                        "high": df["high"].iloc[i],
                        "low": df["low"].iloc[i],
                        "open": df["open"].iloc[i],
                        "close": df["close"].iloc[i],
                        "volume": df["volume"].iloc[i] if "volume" in df.columns else 0,
                        "original_indices": [i],  # 记录原始索引
                    }
                )
                i += 1
                continue

            # 获取前一根合并后的K线
            prev_k = merged_data[-1]
            current_k = df.iloc[i]

            # 判断是否存在包含关系
            # 包含关系：一根K线的最高价和最低价完全包含另一根K线的价格范围
            if (
                prev_k["high"] >= current_k["high"]
                and prev_k["low"] <= current_k["low"]
            ) or (
                current_k["high"] >= prev_k["high"]
                and current_k["low"] <= prev_k["low"]
            ):

                # 确定合并方向
                # 如果前一根K线是上涨的（收盘价 > 开盘价），则向上合并
                # 如果前一根K线是下跌的（收盘价 < 开盘价），则向下合并
                prev_direction = 1 if prev_k["close"] > prev_k["open"] else -1

                # 合并K线
                if prev_direction == 1:  # 向上合并
                    # 高点取最大值，低点取最大值
                    merged_high = max(prev_k["high"], current_k["high"])
                    merged_low = max(prev_k["low"], current_k["low"])
                else:  # 向下合并
                    # 高点取最小值，低点取最小值
                    merged_high = min(prev_k["high"], current_k["high"])
                    merged_low = min(prev_k["low"], current_k["low"])

                # 更新前一根K线的数据
                prev_k["high"] = merged_high
                prev_k["low"] = merged_low
                prev_k["close"] = current_k["close"]
                prev_k["volume"] += current_k["volume"] if "volume" in df.columns else 0
                prev_k["original_indices"].append(i)

                i += 1
            else:
                # 无包含关系，添加新的K线
                merged_data.append(
                    {
                        "time_key": current_k["time_key"],
                        "high": current_k["high"],
                        "low": current_k["low"],
                        "open": current_k["open"],
                        "close": current_k["close"],
                        "volume": current_k["volume"] if "volume" in df.columns else 0,
                        "original_indices": [i],
                    }
                )
                i += 1

        # 转换为DataFrame
        merged_df = pd.DataFrame(merged_data)
        return merged_df

    def identify_fractals(self, df: pd.DataFrame) -> List[Fractal]:
        """
        识别分型结构
        :param df: 包含high, low, time_key列的DataFrame
        :return: 分型列表
        """
        fractals = []

        # 先进行K线合并处理
        merged_df = self._merge_k_lines(df)
        self.merged_df = merged_df  # 保存合并后的数据供后续使用

        # 确保数据按时间排序
        merged_df = merged_df.sort_values("time_key").reset_index(drop=True)

        # 至少需要5根K线才能识别分型
        if len(merged_df) < 5:
            return fractals

        # 遍历中间的K线寻找分型
        for i in range(2, len(merged_df) - 2):
            current_high = merged_df["high"].iloc[i]
            current_low = merged_df["low"].iloc[i]

            # 获取相邻K线的数据
            left1_high = merged_df["high"].iloc[i - 1]
            left2_high = merged_df["high"].iloc[i - 2]
            right1_high = merged_df["high"].iloc[i + 1]
            right2_high = merged_df["high"].iloc[i + 2]

            left1_low = merged_df["low"].iloc[i - 1]
            left2_low = merged_df["low"].iloc[i - 2]
            right1_low = merged_df["low"].iloc[i + 1]
            right2_low = merged_df["low"].iloc[i + 2]

            # 顶分型：中间K线的高点是5根K线中的最高点（允许相等）
            # 检查是否为顶分型
            is_top_fractal = (
                current_high >= left1_high
                and current_high >= left2_high
                and current_high >= right1_high
                and current_high >= right2_high
            )

            if is_top_fractal:
                # 顶分型的低点应该不高于相邻K线的低点（宽松条件）
                # 更宽松的条件：只要不明显违反分型定义即可
                if current_low >= min(left1_low, right1_low):
                    fractals.append(
                        Fractal(
                            index=i,
                            type=FractalType.TOP,
                            price=current_high,
                            timestamp=merged_df["time_key"].iloc[i],
                        )
                    )

            # 底分型：中间K线的低点是5根K线中的最低点（允许相等）
            elif (
                current_low <= left1_low
                and current_low <= left2_low
                and current_low <= right1_low
                and current_low <= right2_low
            ):

                # 底分型的高点应该不低于相邻K线的高点（宽松条件）
                # 更宽松的条件：只要不明显违反分型定义即可
                if current_high <= max(left1_high, right1_high):
                    fractals.append(
                        Fractal(
                            index=i,
                            type=FractalType.BOTTOM,
                            price=current_low,
                            timestamp=merged_df["time_key"].iloc[i],
                        )
                    )

        self.fractals = fractals
        return fractals

    def build_strokes(self, df: pd.DataFrame) -> List[Stroke]:
        """
        根据分型构建笔
        修复版：确保所有有效的分型都被正确连接，不跳过任何分型
        :param df: 包含high, low, time_key列的DataFrame
        :return: 笔列表
        """
        if not self.fractals:
            self.identify_fractals(df)

        strokes = []
        if len(self.fractals) < 2:
            return strokes

        # 使用更全面的方法连接分型，确保不遗漏关键连接
        for i in range(0, len(self.fractals) - 1):
            current = self.fractals[i]

            # 寻找所有可能的有效连接
            for j in range(i + 1, len(self.fractals)):
                next_f = self.fractals[j]

                # 确保方向相反（顶分型连接底分型，或底分型连接顶分型）
                if current.type != next_f.type:
                    # 检查距离（至少2根K线间隔）
                    if abs(next_f.index - current.index) >= 2:
                        # 获取合并后的K线数据
                        merged_df = self.merged_df
                        if merged_df is None:
                            # 如果没有合并数据，使用原始数据
                            merged_df = df

                        # 检查包含关系
                        has_inclusion = self._check_inclusion(
                            merged_df,
                            min(current.index, next_f.index),
                            max(current.index, next_f.index),
                        )

                        # 如果没有包含关系，则可以构建笔
                        if not has_inclusion:
                            direction = 1 if next_f.price > current.price else -1
                            stroke = Stroke(
                                start_index=current.index,
                                end_index=next_f.index,
                                start_price=current.price,
                                end_price=next_f.price,
                                direction=direction,
                                start_timestamp=current.timestamp,
                                end_timestamp=next_f.timestamp,
                            )

                            # 检查是否与已有的笔重叠或冲突
                            if self._is_valid_stroke(stroke, strokes):
                                strokes.append(stroke)
                            break  # 找到第一个有效连接后就停止，避免过度连接

        # 对笔进行排序和清理
        strokes = self._clean_strokes(strokes)

        self.strokes = strokes
        return strokes

    def _is_valid_stroke(
        self, new_stroke: Stroke, existing_strokes: List[Stroke]
    ) -> bool:
        """
        检查新笔是否与已有的笔冲突
        :param new_stroke: 新笔
        :param existing_strokes: 已有的笔列表
        :return: 是否有效
        """
        for stroke in existing_strokes:
            # 检查索引是否重叠
            if not (
                new_stroke.end_index <= stroke.start_index
                or new_stroke.start_index >= stroke.end_index
            ):
                # 有重叠，检查是否是包含关系
                if (
                    new_stroke.start_index <= stroke.start_index
                    and new_stroke.end_index >= stroke.end_index
                ) or (
                    stroke.start_index <= new_stroke.start_index
                    and stroke.end_index >= new_stroke.end_index
                ):
                    # 包含关系，选择更强的笔
                    new_range = abs(new_stroke.end_price - new_stroke.start_price)
                    existing_range = abs(stroke.end_price - stroke.start_price)
                    if new_range > existing_range:
                        existing_strokes.remove(stroke)
                        return True
                    else:
                        return False
        return True

    def _clean_strokes(self, strokes: List[Stroke]) -> List[Stroke]:
        """
        清理笔列表，确保笔的顺序正确且没有冲突
        :param strokes: 笔列表
        :return: 清理后的笔列表
        """
        if len(strokes) <= 1:
            return strokes

        # 按起始索引排序
        strokes.sort(key=lambda x: x.start_index)

        # 确保笔的方向交替
        cleaned_strokes = [strokes[0]]
        for i in range(1, len(strokes)):
            current = strokes[i]
            prev = cleaned_strokes[-1]

            # 确保方向交替
            if current.direction != prev.direction:
                # 确保时间顺序正确
                if current.start_index > prev.start_index:
                    cleaned_strokes.append(current)

        return cleaned_strokes

    def _check_inclusion(self, df: pd.DataFrame, start_idx: int, end_idx: int) -> bool:
        """
        检查指定范围内的K线是否存在包含关系
        :param df: K线数据
        :param start_idx: 起始索引
        :param end_idx: 结束索引
        :return: 是否存在包含关系
        """
        # 检查相邻K线之间的包含关系
        for i in range(start_idx, min(end_idx, len(df) - 1)):
            if i + 1 >= len(df):
                break

            k1 = df.iloc[i]
            k2 = df.iloc[i + 1]

            # 判断是否包含
            # k1包含k2: k1.high >= k2.high 且 k1.low <= k2.low
            # k2包含k1: k2.high >= k1.high 且 k2.low <= k1.low
            if (k1["high"] >= k2["high"] and k1["low"] <= k2["low"]) or (
                k2["high"] >= k1["high"] and k2["low"] <= k1["low"]
            ):
                return True

        return False

    def build_segments(self) -> List[Segment]:
        """
        根据笔构建线段 - 严格按照缠论线段定义
        线段必须由至少3笔构成，且需要满足线段破坏条件
        :return: 线段列表
        """
        segments = []
        if len(self.strokes) < 3:
            return segments

        # 寻找线段起点
        i = 0
        while i < len(self.strokes) - 2:
            # 寻找有效的线段起点（需要至少3笔）
            segment_start = i
            segment_direction = self.strokes[segment_start].direction

            # 检查是否可以形成线段
            j = segment_start + 1
            while j < len(self.strokes):
                # 检查线段破坏条件
                if self._check_segment_break(segment_start, j):
                    # 形成有效线段
                    segment = Segment(
                        start_index=self.strokes[segment_start].start_index,
                        end_index=self.strokes[j].end_index,
                        start_price=self.strokes[segment_start].start_price,
                        end_price=self.strokes[j].end_price,
                        direction=segment_direction,
                        start_timestamp=self.strokes[segment_start].start_timestamp,
                        end_timestamp=self.strokes[j].end_timestamp,
                    )
                    segments.append(segment)
                    i = j  # 从破坏点开始新的线段
                    break
                j += 1

            if j >= len(self.strokes):
                # 没有找到破坏，继续检查
                i += 1

        # 处理最后一段未完成的线段
        if len(segments) == 0 and len(self.strokes) >= 3:
            # 如果没有任何线段被识别，使用最后3笔形成线段
            segment = Segment(
                start_index=self.strokes[0].start_index,
                end_index=self.strokes[-1].end_index,
                start_price=self.strokes[0].start_price,
                end_price=self.strokes[-1].end_price,
                direction=self.strokes[0].direction,
                start_timestamp=self.strokes[0].start_timestamp,
                end_timestamp=self.strokes[-1].end_timestamp,
            )
            segments.append(segment)

        self.segments = segments
        return segments

    def _check_segment_break(self, start_idx: int, break_idx: int) -> bool:
        """
        检查是否形成线段破坏
        :param start_idx: 线段起始笔索引
        :param break_idx: 可能的破坏点索引
        :return: 是否形成破坏
        """
        if break_idx >= len(self.strokes):
            return False

        # 至少需要3笔才能形成线段
        if break_idx - start_idx + 1 < 3:
            return False

        segment_direction = self.strokes[start_idx].direction
        break_stroke = self.strokes[break_idx]

        # 线段破坏条件：
        # 1. 反向笔的价格突破前一线段的高低点
        # 2. 形成新的趋势

        # 计算线段的高低点
        segment_prices = [
            stroke.end_price for stroke in self.strokes[start_idx : break_idx + 1]
        ]
        segment_start_price = self.strokes[start_idx].start_price

        if segment_direction == 1:  # 上涨线段
            # 线段高点
            segment_high = max(segment_prices)
            # 破坏条件：反向笔跌破前低点
            if break_stroke.direction == -1 and break_stroke.end_price < min(
                segment_prices
            ):
                return True
            # 或者反向笔形成新的下跌趋势
            if (
                break_stroke.direction == -1
                and break_stroke.end_price < segment_start_price
            ):
                return True
        else:  # 下跌线段
            # 线段低点
            segment_low = min(segment_prices)
            # 破坏条件：反向笔突破前高点
            if break_stroke.direction == 1 and break_stroke.end_price > max(
                segment_prices
            ):
                return True
            # 或者反向笔形成新的上涨趋势
            if (
                break_stroke.direction == 1
                and break_stroke.end_price > segment_start_price
            ):
                return True

        return False

    def identify_centrals(self) -> List[Central]:
        """
        识别中枢区域
        :return: 中枢列表
        """
        centrals = []

        # 至少需要3笔才能形成中枢
        if len(self.strokes) < 3:
            return centrals

        # 遍历笔，寻找连续3笔的重叠区间
        i = 0
        while i < len(self.strokes) - 2:
            stroke1 = self.strokes[i]
            stroke2 = self.strokes[i + 1]
            stroke3 = self.strokes[i + 2]

            # 检查是否满足中枢形成条件
            # 1. 第1笔和第3笔方向相同
            # 2. 第2笔方向与前两笔相反
            # 3. 存在重叠区间

            if (
                stroke1.direction == stroke3.direction
                and stroke1.direction != stroke2.direction
            ):
                # 计算重叠区间
                if stroke1.direction == 1:  # 向上笔
                    # 重叠区间为：[max(第1笔起点, 第3笔终点), min(第1笔终点, 第3笔起点)]
                    overlap_high = min(stroke1.end_price, stroke3.start_price)
                    overlap_low = max(stroke1.start_price, stroke3.end_price)
                else:  # 向下笔
                    # 重叠区间为：[max(第1笔终点, 第3笔起点), min(第1笔起点, 第3笔终点)]
                    overlap_high = min(stroke1.start_price, stroke3.end_price)
                    overlap_low = max(stroke1.end_price, stroke3.start_price)

                # 检查第2笔是否在重叠区间内
                if stroke2.direction == 1:  # 向上笔
                    second_range_high = stroke2.end_price
                    second_range_low = stroke2.start_price
                else:  # 向下笔
                    second_range_high = stroke2.start_price
                    second_range_low = stroke2.end_price

                # 判断第2笔是否与重叠区间有交集
                if max(overlap_low, second_range_low) <= min(
                    overlap_high, second_range_high
                ):
                    # 形成中枢
                    central = Central(
                        start_index=stroke1.start_index,
                        end_index=stroke3.end_index,
                        high=overlap_high,
                        low=overlap_low,
                        start_timestamp=stroke1.start_timestamp,
                        end_timestamp=stroke3.end_timestamp,
                        strokes=[stroke1, stroke2, stroke3],
                    )
                    centrals.append(central)
                    i += 3  # 跳过已使用的笔
                    continue

            i += 1

        self.centrals = centrals
        return centrals

    def identify_first_buy_point(self, df: pd.DataFrame) -> Optional[int]:
        """
        识别第一类买点
        :param df: K线数据
        :return: 第一类买点的索引，如果没有则返回None
        """
        if not self.centrals or not self.strokes:
            return None

        # 获取最后一个中枢
        last_central = self.centrals[-1]

        # 在中枢下方寻找背驰点
        # 这里简化处理，实际需要计算趋势力度
        for i in range(len(self.strokes) - 1, -1, -1):
            stroke = self.strokes[i]
            # 寻找向下离开中枢的笔
            if stroke.direction == -1 and stroke.start_index >= last_central.end_index:
                # 检查是否存在背驰（简化判断）
                # 实际实现需要比较前后两段走势的力度
                return stroke.end_index

        return None

    def identify_second_buy_point(self, df: pd.DataFrame) -> Optional[int]:
        """
        识别第二类买点
        :param df: K线数据
        :return: 第二类买点的索引，如果没有则返回None
        """
        first_buy_point = self.identify_first_buy_point(df)
        if not first_buy_point:
            return None

        # 第二类买点是第一类买点之后的回踩确认点
        # 在中枢区间内或附近产生的回踩点
        if self.centrals:
            last_central = self.centrals[-1]
            # 寻找第一类买点之后，回到中枢区域的点
            for i in range(first_buy_point + 1, len(df)):
                low_price = df["low"].iloc[i]
                if last_central.low <= low_price <= last_central.high:
                    return i

        return None

    def identify_third_buy_point(self, df: pd.DataFrame) -> Optional[int]:
        """
        识别第三类买点
        :param df: K线数据
        :return: 第三类买点的索引，如果没有则返回None
        """
        if not self.centrals or not self.strokes:
            return None

        # 获取最后一个中枢
        last_central = self.centrals[-1]

        # 第三类买点是离开中枢的笔出现背驰的瞬间
        for i in range(len(self.strokes) - 1, -1, -1):
            stroke = self.strokes[i]
            # 寻找向上离开中枢的笔
            if stroke.direction == 1 and stroke.start_index >= last_central.end_index:
                # 检查是否存在背驰（简化判断）
                return stroke.end_index

        return None

    def check_divergence(self, df: pd.DataFrame, start_idx: int, end_idx: int) -> bool:
        """
        检查两段走势是否存在背驰
        :param df: K线数据
        :param start_idx: 起始索引
        :param end_idx: 结束索引
        :return: 是否存在背驰
        """
        # 使用合并后的K线数据计算背驰
        if self.merged_df is None:
            return False

        # 获取指定范围内的K线数据
        range_df = self.merged_df[
            (self.merged_df.index >= start_idx) & (self.merged_df.index <= end_idx)
        ]

        if len(range_df) < 2:
            return False

        # 计算价格变化和成交量变化（简化版背驰检测）
        price_change = abs(range_df["close"].iloc[-1] - range_df["close"].iloc[0])
        volume_change = range_df["volume"].sum() if "volume" in range_df.columns else 0

        # 这里应该计算技术指标的背驰，比如MACD柱状图面积等
        # 简化处理：如果价格创新高但成交量萎缩，则认为可能有背驰
        # 实际应用中需要更复杂的指标计算

        # 简化判断：当价格上涨但成交量下降时判断为背驰
        if (
            len(range_df) > 0
            and range_df["close"].iloc[-1] > range_df["close"].iloc[0]
            and volume_change
            < (range_df["volume"].mean() if "volume" in range_df.columns else 0) * 0.8
        ):
            return True

        return False

    def process(self, df: pd.DataFrame) -> dict:
        """
        完整处理流程，使用合并后的K线数据
        :param df: K线数据
        :return: 包含所有缠论结构的字典
        """
        # 识别分型
        self.identify_fractals(df)

        # 构建笔
        self.build_strokes(df)

        # 构建线段
        self.build_segments()

        # 识别中枢
        self.identify_centrals()

        return {
            "fractals": self.fractals,
            "strokes": self.strokes,
            "segments": self.segments,
            "centrals": self.centrals,
        }
