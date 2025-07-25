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
