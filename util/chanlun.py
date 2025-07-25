# util/chanlun.py
import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class FractalType(Enum):
    TOP = "top"
    BOTTOM = "bottom"


@dataclass
class Fractal:
    index: int
    type: FractalType
    price: float


@dataclass
class Stroke:
    """笔结构"""

    start_index: int
    end_index: int
    start_price: float
    end_price: float
    direction: int  # 1 for up, -1 for down


@dataclass
class Central:
    """中枢结构"""

    start_index: int
    end_index: int
    high: float
    low: float
    level: int = 1  # 中枢级别


class ChanlunProcessor:
    def __init__(self):
        self.merged_df: Optional[pd.DataFrame] = None
        self.fractals: List[Fractal] = []
        self.strokes: List[Stroke] = []
        self.segments: List[Stroke] = []  # 线段
        self.centrals: List[Central] = []  # 中枢

    def _merge_k_lines(self, df: pd.DataFrame):
        """合并K线，处理包含关系"""
        if df.empty:
            self.merged_df = pd.DataFrame()
            return

        df = df.sort_values("time_key").reset_index(drop=True)

        merged_data = []
        if len(df) > 0:
            kline = df.iloc[0].to_dict()
            kline["original_indices"] = [0]
            merged_data.append(kline)

        for i in range(1, len(df)):
            current_k = df.iloc[i]
            last_merged_k = merged_data[-1]

            is_contained = (
                last_merged_k["high"] >= current_k["high"]
                and last_merged_k["low"] <= current_k["low"]
            )
            is_containing = (
                current_k["high"] >= last_merged_k["high"]
                and current_k["low"] <= last_merged_k["low"]
            )

            if is_contained or is_containing:
                direction = 1 if last_merged_k["close"] >= last_merged_k["open"] else -1

                if direction == 1:
                    last_merged_k["high"] = max(
                        last_merged_k["high"], current_k["high"]
                    )
                    last_merged_k["low"] = max(last_merged_k["low"], current_k["low"])
                else:
                    last_merged_k["high"] = min(
                        last_merged_k["high"], current_k["high"]
                    )
                    last_merged_k["low"] = min(last_merged_k["low"], current_k["low"])

                last_merged_k["close"] = current_k["close"]
                last_merged_k["time_key"] = current_k["time_key"]
                last_merged_k["original_indices"].append(i)
            else:
                new_kline = current_k.to_dict()
                new_kline["original_indices"] = [i]
                merged_data.append(new_kline)

        self.merged_df = pd.DataFrame(merged_data)

    def identify_fractals(self) -> List[Fractal]:
        """识别分型结构"""
        if self.merged_df is None or len(self.merged_df) < 3:
            return []

        fractals = []
        for i in range(1, len(self.merged_df) - 1):
            is_top = (
                self.merged_df["high"].iloc[i] > self.merged_df["high"].iloc[i - 1]
                and self.merged_df["high"].iloc[i] > self.merged_df["high"].iloc[i + 1]
                and self.merged_df["low"].iloc[i] > self.merged_df["low"].iloc[i - 1]
                and self.merged_df["low"].iloc[i] > self.merged_df["low"].iloc[i + 1]
            )
            if is_top:
                fractals.append(
                    Fractal(
                        index=i,
                        type=FractalType.TOP,
                        price=self.merged_df["high"].iloc[i],
                    )
                )

            is_bottom = (
                self.merged_df["low"].iloc[i] < self.merged_df["low"].iloc[i - 1]
                and self.merged_df["low"].iloc[i] < self.merged_df["low"].iloc[i + 1]
                and self.merged_df["high"].iloc[i] < self.merged_df["high"].iloc[i - 1]
                and self.merged_df["high"].iloc[i] < self.merged_df["high"].iloc[i + 1]
            )
            if is_bottom:
                fractals.append(
                    Fractal(
                        index=i,
                        type=FractalType.BOTTOM,
                        price=self.merged_df["low"].iloc[i],
                    )
                )

        self.fractals = fractals
        return fractals

    def build_strokes(self) -> List[Stroke]:
        """构建笔"""
        if not self.fractals:
            return []

        strokes = []
        all_fractals = sorted(self.fractals, key=lambda x: x.index)

        if len(all_fractals) < 2:
            return []

        for i in range(1, len(all_fractals)):
            prev_fractal = all_fractals[i - 1]
            curr_fractal = all_fractals[i]

            if prev_fractal.type != curr_fractal.type:
                direction = 1 if curr_fractal.type == FractalType.TOP else -1
                stroke = Stroke(
                    start_index=prev_fractal.index,
                    end_index=curr_fractal.index,
                    start_price=prev_fractal.price,
                    end_price=curr_fractal.price,
                    direction=direction,
                )
                strokes.append(stroke)

        self.strokes = strokes
        return strokes

    def build_centrals(self) -> List[Central]:
        """构建中枢"""
        if len(self.strokes) < 3:
            return []

        centrals = []

        for i in range(len(self.strokes) - 2):
            stroke1 = self.strokes[i]
            stroke2 = self.strokes[i + 1]
            stroke3 = self.strokes[i + 2]

            min_high = min(stroke1.end_price, stroke2.end_price, stroke3.end_price)
            max_low = max(stroke1.end_price, stroke2.end_price, stroke3.end_price)

            if min_high > max_low:
                central = Central(
                    start_index=stroke1.start_index,
                    end_index=stroke3.end_index,
                    high=min_high,
                    low=max_low,
                )
                centrals.append(central)

        self.centrals = centrals
        return centrals

    def build_segments(self) -> List[Stroke]:
        """构建线段（将多个笔合并成趋势线段）"""
        if len(self.strokes) < 3:
            self.segments = []
            return []

        segments = []
        
        # 线段构建逻辑：
        # 1. 从第一个笔开始，确定初始方向
        # 2. 持续跟踪笔的走势，直到出现反向突破
        # 3. 反向突破确认后，形成一个线段
        
        i = 0
        while i < len(self.strokes):
            # 至少需要3笔才能开始构建线段
            if i + 2 >= len(self.strokes):
                break
                
            # 以当前笔作为线段的起点
            start_stroke = self.strokes[i]
            direction = start_stroke.direction
            
            # 寻找线段的终点（需要满足线段定义）
            # 线段至少包含3笔，且需要有明确的破坏点
            segment_end_idx = i
            
            # 向前查找，确定线段的范围
            for j in range(i + 1, len(self.strokes)):
                # 检查是否满足线段破坏条件
                # 对于向上线段，破坏条件是出现向下笔突破最后一个向上笔的低点
                # 对于向下线段，破坏条件是出现向上笔突破最后一个向下笔的高点
                if direction == 1:  # 向上线段
                    if self.strokes[j].direction == -1:  # 出现向下笔
                        # 检查是否突破了线段最后一个向上笔的低点
                        last_up_stroke = None
                        for k in range(i, j):
                            if self.strokes[k].direction == 1:
                                last_up_stroke = self.strokes[k]
                        
                        if last_up_stroke and self.strokes[j].end_price < last_up_stroke.start_price:
                            # 线段被破坏，确认线段结束
                            segment_end_idx = j - 1
                            break
                else:  # 向下线段
                    if self.strokes[j].direction == 1:  # 出现向上笔
                        # 检查是否突破了线段最后一个向下笔的高点
                        last_down_stroke = None
                        for k in range(i, j):
                            if self.strokes[k].direction == -1:
                                last_down_stroke = self.strokes[k]
                        
                        if last_down_stroke and self.strokes[j].end_price > last_down_stroke.start_price:
                            # 线段被破坏，确认线段结束
                            segment_end_idx = j - 1
                            break
            
            # 如果找到了足够的笔来构成线段（至少3笔）
            if segment_end_idx >= i + 2:
                # 创建线段
                end_stroke = self.strokes[segment_end_idx]
                segment = Stroke(
                    start_index=start_stroke.start_index,
                    end_index=end_stroke.end_index,
                    start_price=start_stroke.start_price,
                    end_price=end_stroke.end_price,
                    direction=direction,
                )
                segments.append(segment)
                
                # 从下一个可能的线段起点开始继续处理
                i = segment_end_idx + 1
            else:
                # 没有找到合适的线段，继续下一个笔
                i += 1

        self.segments = segments
        return segments

    def identify_first_buy_point(self, df: pd.DataFrame) -> Optional[int]:
        """识别第一类买点"""
        if len(self.centrals) < 2:
            return None

        last_central = self.centrals[-1]
        prev_central = self.centrals[-2]

        if last_central.low < prev_central.low:
            if len(df) > 20:
                recent_low = df["close"].iloc[-5:].min()
                prev_low = df["close"].iloc[-20:-5].min()

                if recent_low < prev_low:
                    return len(df) - 1

        return None

    def identify_second_buy_point(self, df: pd.DataFrame) -> Optional[int]:
        """识别第二类买点"""
        if len(self.centrals) < 1:
            return None

        last_central = self.centrals[-1]
        if len(self.strokes) >= 3:
            last_stroke = self.strokes[-1]
            if last_stroke.direction == -1:
                if last_stroke.end_price > last_central.low:
                    return len(df) - 1

        return None

    def identify_third_buy_point(self, df: pd.DataFrame) -> Optional[int]:
        """识别第三类买点"""
        if len(self.centrals) < 1:
            return None

        last_central = self.centrals[-1]
        if len(self.strokes) >= 2:
            last_stroke = self.strokes[-1]
            if last_stroke.direction == -1:
                if last_central.low <= last_stroke.end_price <= last_central.high:
                    return len(df) - 1

        return None

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """完整的缠论处理流程"""
        try:
            self._merge_k_lines(df)
            self.identify_fractals()
            self.build_strokes()
            self.build_segments()
            self.build_centrals()

            return {
                "merged_df": self.merged_df,
                "fractals": self.fractals,
                "strokes": self.strokes,
                "segments": self.segments,
                "centrals": self.centrals,
            }
        except Exception as e:
            print(f"缠论处理出错: {e}")
            return {
                "merged_df": pd.DataFrame(),
                "fractals": [],
                "strokes": [],
                "segments": [],
                "centrals": [],
            }
