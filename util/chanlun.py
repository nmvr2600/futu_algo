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
    time_key: pd.Timestamp = None  # 关键K线的时间戳，作为唯一标识
    related_time_keys: List[pd.Timestamp] = None  # 关联K线的时间戳列表（可选）
    idx: int = 0  # 分型编号，不管是顶分型还是底分型，依次编号为1,2,3,4...
    
    def __post_init__(self):
        if self.related_time_keys is None:
            self.related_time_keys = []


@dataclass
class Stroke:
    """笔结构"""

    start_index: int
    end_index: int
    start_price: float
    end_price: float
    direction: int  # 1 for up, -1 for down
    start_time_key: pd.Timestamp = None  # 起始分型的时间戳标识
    end_time_key: pd.Timestamp = None  # 结束分型的时间戳标识
    idx: int = 0  # 笔序号 1,2,3...
    fractal_start: int = 0  # 起始分形序号
    fractal_end: int = 0  # 结束分形序号


@dataclass
class Central:
    """中枢结构"""

    start_index: int
    end_index: int
    high: float
    low: float
    start_time_key: pd.Timestamp = None  # 起始笔的时间戳标识
    end_time_key: pd.Timestamp = None  # 结束笔的时间戳标识
    level: int = 1  # 中枢级别
    strokes: Optional[List[Stroke]] = None


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
        fractal_count = 0  # 分型编号计数器
        for i in range(1, len(self.merged_df) - 1):
            is_top = (
                self.merged_df["high"].iloc[i] > self.merged_df["high"].iloc[i - 1]
                and self.merged_df["high"].iloc[i] > self.merged_df["high"].iloc[i + 1]
                and self.merged_df["low"].iloc[i] > self.merged_df["low"].iloc[i - 1]
                and self.merged_df["low"].iloc[i] > self.merged_df["low"].iloc[i + 1]
            )
            if is_top:
                fractal_count += 1
                fractals.append(
                    Fractal(
                        index=i,
                        type=FractalType.TOP,
                        price=self.merged_df["high"].iloc[i],
                        time_key=self.merged_df["time_key"].iloc[i],  # 添加time_key标识
                        idx=fractal_count,  # 添加分型编号
                    )
                )

            is_bottom = (
                self.merged_df["low"].iloc[i] < self.merged_df["low"].iloc[i - 1]
                and self.merged_df["low"].iloc[i] < self.merged_df["low"].iloc[i + 1]
                and self.merged_df["high"].iloc[i] < self.merged_df["high"].iloc[i - 1]
                and self.merged_df["high"].iloc[i] < self.merged_df["high"].iloc[i + 1]
            )
            if is_bottom:
                fractal_count += 1
                fractals.append(
                    Fractal(
                        index=i,
                        type=FractalType.BOTTOM,
                        price=self.merged_df["low"].iloc[i],
                        time_key=self.merged_df["time_key"].iloc[i],  # 添加time_key标识
                        idx=fractal_count,  # 添加分型编号
                    )
                )

        self.fractals = fractals
        return fractals

    def build_strokes(self) -> List[Stroke]:
        """构建笔（带索引追踪）"""
        if not self.fractals:
            return []

        strokes = []
        all_fractals = sorted(self.fractals, key=lambda x: x.index)

        if len(all_fractals) < 2:
            return []

        for i in range(1, len(all_fractals)):
            prev_fractal = all_fractals[i - 1]
            curr_fractal = all_fractals[i]

            # 检查分型索引是否在合并数据范围内
            if (prev_fractal.index >= len(self.merged_df) or 
                curr_fractal.index >= len(self.merged_df) or
                prev_fractal.index < 0 or curr_fractal.index < 0):
                continue

            if prev_fractal.type != curr_fractal.type:
                direction = 1 if curr_fractal.type == FractalType.TOP else -1

                # 获取原始K线数据中的实际价格
                original_start_indices = self.merged_df.iloc[prev_fractal.index][
                    "original_indices"
                ]
                original_end_indices = self.merged_df.iloc[curr_fractal.index][
                    "original_indices"
                ]

                # 使用原始K线数据中的实际价格
                if direction == 1:  # 上涨笔
                    start_price = self.merged_df["low"].iloc[prev_fractal.index]
                    end_price = self.merged_df["high"].iloc[curr_fractal.index]
                else:  # 下跌笔
                    start_price = self.merged_df["high"].iloc[prev_fractal.index]
                    end_price = self.merged_df["low"].iloc[curr_fractal.index]

                stroke = Stroke(
                    start_index=prev_fractal.index,
                    end_index=curr_fractal.index,
                    start_price=start_price,
                    end_price=end_price,
                    direction=direction,
                    start_time_key=prev_fractal.time_key,  # 添加起始分型time_key
                    end_time_key=curr_fractal.time_key,  # 添加结束分型time_key
                    idx=len(strokes) + 1,  # 笔序号 1,2,3...
                    fractal_start=prev_fractal.idx,  # 起始分形序号
                    fractal_end=curr_fractal.idx,  # 结束分形序号
                )
                strokes.append(stroke)

        self.strokes = strokes
        return strokes

    def build_centrals(self) -> List[Central]:
        """构建中枢"""
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
                # 中枢的重叠区间是第一笔和第三笔的重叠部分
                if stroke1.direction == 1:  # 上涨->下跌->上涨
                    # 第一笔区间: [stroke1.start_price, stroke1.end_price]
                    # 第三笔区间: [stroke3.start_price, stroke3.end_price]
                    overlap_high = min(stroke1.end_price, stroke3.end_price)
                    overlap_low = max(stroke1.start_price, stroke3.start_price)
                else:  # 下跌->上涨->下跌
                    # 第一笔区间: [stroke1.end_price, stroke1.start_price]
                    # 第三笔区间: [stroke3.start_price, stroke3.end_price]
                    overlap_high = min(stroke1.start_price, stroke3.start_price)
                    overlap_low = max(stroke1.end_price, stroke3.end_price)

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
                        start_time_key=stroke1.start_time_key,  # 添加起始笔time_key
                        end_time_key=stroke3.end_time_key,  # 添加结束笔time_key
                        strokes=[stroke1, stroke2, stroke3],
                    )
                    centrals.append(central)
                    i += 3  # 跳过已使用的笔
                    continue

            i += 1

        # 合并所有有重叠的中枢
        if len(centrals) > 1:
            # 使用并查集的思想来合并中枢
            # 初始化每个中枢为一个独立的集合
            parent = list(range(len(centrals)))
            
            def find(x):
                if parent[x] != x:
                    parent[x] = find(parent[x])  # 路径压缩
                return parent[x]
            
            def union(x, y):
                root_x = find(x)
                root_y = find(y)
                if root_x != root_y:
                    parent[root_y] = root_x
            
            # 检查所有中枢对，如果有重叠则合并它们
            for i in range(len(centrals)):
                for j in range(i+1, len(centrals)):
                    # 检查两个中枢是否有重叠
                    if max(centrals[i].low, centrals[j].low) <= min(centrals[i].high, centrals[j].high):
                        union(i, j)
            
            # 根据并查集的结果，将属于同一集合的中枢合并
            merged_groups = {}
            for i in range(len(centrals)):
                root = find(i)
                if root not in merged_groups:
                    merged_groups[root] = []
                merged_groups[root].append(centrals[i])
            
            # 创建合并后的中枢
            merged_centrals = []
            for group in merged_groups.values():
                if len(group) == 1:
                    # 单独的中枢，不需要合并
                    merged_centrals.append(group[0])
                else:
                    # 需要合并的中枢组
                    # 合并后的中枢范围是所有中枢的并集
                    high = max(central.high for central in group)
                    low = min(central.low for central in group)
                    start_index = min(central.start_index for central in group)
                    end_index = max(central.end_index for central in group)
                    
                    # 合并所有笔
                    all_strokes = []
                    for central in group:
                        if central.strokes:
                            all_strokes.extend(central.strokes)
                    
                    merged_central = Central(
                        start_index=start_index,
                        end_index=end_index,
                        high=high,
                        low=low,
                        start_time_key=group[0].start_time_key,  # 添加起始笔time_key
                        end_time_key=group[-1].end_time_key,  # 添加结束笔time_key
                        strokes=all_strokes,
                    )
                    merged_centrals.append(merged_central)
            
            centrals = merged_centrals

        self.centrals = centrals
        return centrals

    def build_segments(self) -> List[Stroke]:
        """构建线段（确保连续性，消除断裂）"""
        segments = []
        segment_count = 0
        
        # 核心策略：确保每个笔都被线段覆盖，无间隙
        if not self.strokes:
            self.segments = []
            return []
        
        # 如果只有1-2笔，直接创建覆盖所有笔的线段
        if len(self.strokes) <= 3:
            if len(self.strokes) >= 1:
                segment_count += 1
                segment = Stroke(
                    start_index=self.strokes[0].start_index,
                    end_index=self.strokes[-1].end_index,
                    start_price=self.strokes[0].start_price,
                    end_price=self.strokes[-1].end_price,
                    direction=self.strokes[0].direction,
                    start_time_key=self.strokes[0].start_time_key,
                    end_time_key=self.strokes[-1].end_time_key,
                    idx=segment_count,
                    fractal_start=self.strokes[0].fractal_start,
                    fractal_end=self.strokes[-1].fractal_end,
                )
                segments.append(segment)
                self.segments = segments
                return segments
        
        # 对于多条笔，采用连续覆盖策略
        current_start = 0
        
        while current_start < len(self.strokes):
            # 确定当前线段的方向
            direction = self.strokes[current_start].direction
            
            # 寻找合适的终点
            segment_end = current_start
            
            # 策略1：寻找下一个方向反转点
            for j in range(current_start + 1, len(self.strokes)):
                if self.strokes[j].direction != direction:
                    # 找到方向反转，当前线段终点为前一个笔
                    segment_end = j - 1
                    break
            else:
                # 没有找到方向反转，覆盖到末尾
                segment_end = len(self.strokes) - 1
            
            # 确保线段至少包含当前笔
            segment_end = max(segment_end, current_start)
            
            if segment_end >= current_start:
                # 创建线段
                start_stroke = self.strokes[current_start]
                end_stroke = self.strokes[segment_end]
                
                segment_count += 1
                segment = Stroke(
                    start_index=start_stroke.start_index,
                    end_index=end_stroke.end_index,
                    start_price=start_stroke.start_price,
                    end_price=end_stroke.end_price,
                    direction=direction,
                    start_time_key=start_stroke.start_time_key,
                    end_time_key=end_stroke.end_time_key,
                    idx=segment_count,
                    fractal_start=start_stroke.fractal_start,
                    fractal_end=end_stroke.fractal_end,
                )
                segments.append(segment)
                
                # 下一个线段从当前线段终点开始，确保连续性
                current_start = segment_end
                if current_start >= len(self.strokes) - 1:
                    break
        
        # 确保最后一个笔被覆盖
        if segments and segments[-1].end_index < self.strokes[-1].end_index:
            # 创建最后一个线段覆盖剩余部分
            start_stroke = self.strokes[segments[-1].end_index + 1] if segments[-1].end_index + 1 < len(self.strokes) else segments[-1]
            end_stroke = self.strokes[-1]
            
            segment_count += 1
            segment = Stroke(
                start_index=start_stroke.start_index,
                end_index=end_stroke.end_index,
                start_price=start_stroke.start_price,
                end_price=end_stroke.end_price,
                direction=start_stroke.direction,
                start_time_key=start_stroke.start_time_key,
                end_time_key=end_stroke.end_time_key,
                idx=segment_count,
                fractal_start=start_stroke.fractal_start,
                fractal_end=end_stroke.fractal_end,
            )
            segments.append(segment)

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
            print("开始处理K线数据...")
            self._merge_k_lines(df)
            print(
                f"合并K线完成，共 {len(self.merged_df) if self.merged_df is not None else 0} 根K线"
            )

            self.identify_fractals()
            print(f"识别分型完成，共 {len(self.fractals)} 个分型")
            # 输出分型信息
            for fractal in self.fractals:
                type_str = "顶" if fractal.type == FractalType.TOP else "底"
                print(
                    f"  分型 {fractal.idx}: {type_str}分型，索引={fractal.index}, 价格={fractal.price:.2f}"
                )

            self.build_strokes()
            print(f"构建笔完成，共 {len(self.strokes)} 笔")
            # 输出笔信息
            for stroke in self.strokes:
                direction_str = "上涨" if stroke.direction == 1 else "下跌"
                print(
                    f"  笔 {stroke.idx}: [{stroke.fractal_start},{stroke.fractal_end}], "
                    f"{direction_str} {stroke.start_price:.2f}->{stroke.end_price:.2f}, "
                    f"索引 {stroke.start_index}->{stroke.end_index}"
                )

            self.build_segments()
            print(f"构建线段完成，共 {len(self.segments)} 个线段")
            # 输出线段信息
            for segment in self.segments:
                direction_str = "上涨" if segment.direction == 1 else "下跌"
                print(
                    f"  线段 {segment.idx}: [{segment.fractal_start},{segment.fractal_end}], "
                    f"{direction_str} {segment.start_price:.2f}->{segment.end_price:.2f}, "
                    f"索引 {segment.start_index}->{segment.end_index}"
                )

            self.build_centrals()
            print(f"构建中枢完成，共 {len(self.centrals)} 个中枢")

            return {
                "merged_df": self.merged_df,
                "fractals": self.fractals,
                "strokes": self.strokes,
                "segments": self.segments,
                "centrals": self.centrals,
                "index_mapping": (
                    {i: row["original_indices"] for i, row in self.merged_df.iterrows()}
                    if self.merged_df is not None
                    else {}
                ),
            }
        except Exception as e:
            print(f"缠论处理出错: {e}")
            import traceback

            traceback.print_exc()
            return {
                "merged_df": pd.DataFrame(),
                "fractals": [],
                "strokes": [],
                "segments": [],
                "centrals": [],
            }
