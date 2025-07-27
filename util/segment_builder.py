#!/usr/bin/env python3
"""
线段构建器
实现正确的缠论线段构建逻辑
"""

from typing import List, Tuple, Optional
from util.chanlun import Stroke


class SegmentBuilder:
    """线段构建器"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def can_form_segment_start(self, strokes: List[Stroke], start_index: int) -> bool:
        """
        检查是否能在线段起点形成有效的线段开始
        
        Args:
            strokes: 笔列表
            start_index: 起始索引
            
        Returns:
            bool: 是否能形成线段起点
        """
        # 检查是否有足够的笔
        if start_index > len(strokes) - 3:
            return False
        
        # 获取前三笔
        stroke1 = strokes[start_index]
        stroke2 = strokes[start_index + 1]
        stroke3 = strokes[start_index + 2]
        
        # 检查方向交替性：第一笔和第三笔同向，第二笔反向
        if not (stroke1.direction == stroke3.direction and stroke1.direction != stroke2.direction):
            return False
        
        # 计算每笔的价格区间
        if stroke1.direction == 1:  # 向上笔
            range1 = (stroke1.start_price, stroke1.end_price)
            range2 = (stroke2.end_price, stroke2.start_price)  # 向下笔，注意区间反转
            range3 = (stroke3.start_price, stroke3.end_price)
        else:  # 向下笔
            range1 = (stroke1.end_price, stroke1.start_price)
            range2 = (stroke2.start_price, stroke2.end_price)  # 向上笔
            range3 = (stroke3.end_price, stroke3.start_price)
        
        # 计算重叠区间
        overlap_low = max(min(range1), min(range2), min(range3))
        overlap_high = min(max(range1), max(range2), max(range3))
        
        # 检查是否有重叠
        return overlap_low <= overlap_high
    
    def find_segment_break_point(self, strokes: List[Stroke], segment_start: int, segment_direction: int) -> Optional[int]:
        """
        找到线段的破坏点
        
        Args:
            strokes: 笔列表
            segment_start: 线段起始笔索引
            segment_direction: 线段方向
            
        Returns:
            Optional[int]: 破坏点索引，None表示未找到破坏
        """
        # 检查索引有效性
        if segment_start >= len(strokes):
            return None
        
        # 找到当前线段的极值点
        segment_high = None
        segment_low = None
        
        if segment_direction == 1:  # 上涨线段
            # 找到线段中的最高点
            segment_high = strokes[segment_start].start_price
            for i in range(segment_start, len(strokes)):
                if strokes[i].direction != segment_direction:
                    break
                segment_high = max(segment_high, strokes[i].start_price, strokes[i].end_price)
        else:  # 下跌线段
            # 找到线段中的最低点
            segment_low = strokes[segment_start].start_price
            for i in range(segment_start, len(strokes)):
                if strokes[i].direction != segment_direction:
                    break
                segment_low = min(segment_low, strokes[i].start_price, strokes[i].end_price)
        
        # 查找破坏点
        for i in range(segment_start, len(strokes)):
            # 跳过同向笔
            if strokes[i].direction == segment_direction:
                continue
            
            # 遇到反向笔，检查是否构成破坏
            if segment_direction == 1:  # 原线段是上涨线段
                # 反向笔（下跌）需要突破原线段的最低点
                if segment_low is not None:
                    break_end_price = strokes[i].end_price
                    if break_end_price < segment_low:
                        return i
            else:  # 原线段是下跌线段
                # 反向笔（上涨）需要突破原线段的最高点
                if segment_high is not None:
                    break_end_price = strokes[i].end_price
                    if break_end_price > segment_high:
                        return i
        
        return None
    
    def find_segment_end_by_growth(self, strokes: List[Stroke], start_idx: int) -> int:
        """
        通过线段生长找到线段终点
        
        Args:
            strokes: 笔列表
            start_idx: 起始索引
            
        Returns:
            int: 线段终点索引
        """
        if start_idx >= len(strokes) - 1:
            return start_idx
        
        # 线段方向由第一笔决定
        segment_direction = strokes[start_idx].direction
        
        # 找到所有同向的连续笔
        i = start_idx
        while i < len(strokes) and strokes[i].direction == segment_direction:
            i += 1
        
        # 返回最后一个同向笔的索引
        return i - 1 if i > start_idx else start_idx
    
    def build_segments(self, strokes: List[Stroke]) -> List[Stroke]:
        """
        构建线段主逻辑 - 正确的缠论实现
        
        Args:
            strokes: 笔列表
            
        Returns:
            List[Stroke]: 线段列表
        """
        segments = []
        if len(strokes) < 3:
            return segments
        
        # 正确的缠论线段构建算法
        i = 0
        segment_count = 0
        
        while i <= len(strokes) - 3:
            # 检查是否能形成线段起点（前三笔满足条件）
            can_form = self.can_form_segment_start(strokes, i)
            # print(f"检查起点 {i}: {'可以形成' if can_form else '不能形成'}")
            
            if not can_form:
                i += 1
                continue
            
            # 找到线段的实际终点
            segment_end = self._find_actual_segment_end(strokes, i)
            # print(f"起点 {i} 的线段终点: {segment_end}")
            
            # 确保至少包含3笔
            if segment_end >= i + 2:
                # 创建线段
                start_stroke = strokes[i]
                end_stroke = strokes[segment_end]
                
                segment_count += 1
                segment = Stroke(
                    start_index=start_stroke.start_index,
                    end_index=end_stroke.end_index,
                    start_price=start_stroke.start_price,
                    end_price=end_stroke.end_price,
                    direction=start_stroke.direction,
                    idx=segment_count,
                    fractal_start=start_stroke.fractal_start,
                    fractal_end=end_stroke.fractal_end
                )
                segments.append(segment)
                # print(f"创建线段 {segment_count}: 起点{i} 到终点{segment_end}")
                
                # 移动到线段结束后的位置继续查找
                i = segment_end + 1
            else:
                i += 1
        
        # 如果没有找到满足条件的线段，使用简化处理
        if not segments and len(strokes) >= 3:
            # print("使用简化处理")
            # 将连续同向笔合并为线段
            i = 0
            while i < len(strokes):
                current_direction = strokes[i].direction
                j = i
                # 找到连续同向笔
                while j < len(strokes) and strokes[j].direction == current_direction:
                    j += 1
                
                if j > i:
                    # 创建线段
                    start_stroke = strokes[i]
                    end_stroke = strokes[j-1]
                    
                    segment_count += 1
                    segment = Stroke(
                        start_index=start_stroke.start_index,
                        end_index=end_stroke.end_index,
                        start_price=start_stroke.start_price,
                        end_price=end_stroke.end_price,
                        direction=current_direction,
                        idx=segment_count,
                        fractal_start=start_stroke.fractal_start,
                        fractal_end=end_stroke.fractal_end
                    )
                    segments.append(segment)
                
                i = j
        
        return segments
    
    def _find_actual_segment_end(self, strokes: List[Stroke], start_idx: int) -> int:
        """
        找到线段的实际终点（考虑破坏点）
        
        Args:
            strokes: 笔列表
            start_idx: 起始索引
            
        Returns:
            int: 线段终点索引
        """
        if start_idx >= len(strokes) - 1:
            return start_idx
        
        # 线段方向由起始笔决定
        segment_direction = strokes[start_idx].direction
        
        # 线段需要包含多个同向笔，查找所有连续同向笔
        i = start_idx
        while i < len(strokes) and strokes[i].direction == segment_direction:
            i += 1
        
        # 返回最后一个同向笔的索引
        natural_end = i - 1 if i > start_idx else start_idx
        
        # 确保至少有3笔
        min_end = min(start_idx + 2, len(strokes) - 1)
        if natural_end < min_end:
            natural_end = min_end
        
        # 检查是否有破坏点在线段内部
        break_point = self.find_segment_break_point(strokes, start_idx, segment_direction)
        if break_point is not None and break_point <= natural_end and break_point > start_idx:
            # 破坏点在当前线段范围内，线段应该在此结束
            return break_point - 1
        
        return natural_end