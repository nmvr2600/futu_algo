#!/usr/bin/env python3
"""
线段数据验证器
验证线段构建的正确性
"""

from typing import List, Tuple
from util.chanlun import Stroke


class SegmentValidator:
    """线段验证器"""
    
    @staticmethod
    def validate_stroke_continuity(strokes: List[Stroke]) -> Tuple[bool, List[str]]:
        """
        验证笔是否首尾相接
        
        Args:
            strokes: 笔列表
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        errors = []
        if len(strokes) < 2:
            return True, errors
        
        for i in range(1, len(strokes)):
            prev_stroke = strokes[i-1]
            curr_stroke = strokes[i]
            
            if prev_stroke.end_index != curr_stroke.start_index:
                errors.append(
                    f"笔不连续: 笔{prev_stroke.idx}终点索引{prev_stroke.end_index} "
                    f"!= 笔{curr_stroke.idx}起点索引{curr_stroke.start_index}"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_stroke_direction_alternation(strokes: List[Stroke]) -> Tuple[bool, List[str]]:
        """
        验证笔方向是否交替
        
        Args:
            strokes: 笔列表
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        errors = []
        if len(strokes) < 2:
            return True, errors
        
        for i in range(1, len(strokes)):
            prev_stroke = strokes[i-1]
            curr_stroke = strokes[i]
            
            if prev_stroke.direction == curr_stroke.direction:
                direction_str = "上涨" if prev_stroke.direction == 1 else "下跌"
                errors.append(
                    f"笔方向未交替: 笔{prev_stroke.idx}和笔{curr_stroke.idx}方向相同({direction_str})"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_segment_continuity(segments: List[Stroke]) -> Tuple[bool, List[str]]:
        """
        验证线段是否首尾相接
        
        Args:
            segments: 线段列表（使用Stroke结构）
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        errors = []
        if len(segments) < 2:
            return True, errors
        
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            
            if prev_segment.end_index != curr_segment.start_index:
                errors.append(
                    f"线段不连续: 线段{prev_segment.idx}终点索引{prev_segment.end_index} "
                    f"!= 线段{curr_segment.idx}起点索引{curr_segment.start_index}"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_segment_direction_alternation(segments: List[Stroke]) -> Tuple[bool, List[str]]:
        """
        验证线段方向是否交替
        
        Args:
            segments: 线段列表（使用Stroke结构）
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        errors = []
        if len(segments) < 2:
            return True, errors
        
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            
            if prev_segment.direction == curr_segment.direction:
                direction_str = "上涨" if prev_segment.direction == 1 else "下跌"
                errors.append(
                    f"线段方向未交替: 线段{prev_segment.idx}和线段{curr_segment.idx}方向相同({direction_str})"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_segment_composition(segments: List[Stroke], original_strokes: List[Stroke]) -> Tuple[bool, List[str]]:
        """
        验证线段构成（每线段至少3笔）
        
        Args:
            segments: 线段列表
            original_strokes: 原始笔列表
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        errors = []
        
        for segment in segments:
            # 计算线段包含的笔数
            stroke_count = 0
            for stroke in original_strokes:
                if (stroke.start_index >= segment.start_index and 
                    stroke.end_index <= segment.end_index):
                    stroke_count += 1
            
            if stroke_count < 3:
                errors.append(
                    f"线段{segment.idx}包含笔数不足: {stroke_count} < 3"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_all(strokes: List[Stroke], segments: List[Stroke]) -> Tuple[bool, List[str]]:
        """
        综合验证所有条件
        
        Args:
            strokes: 原始笔列表
            segments: 线段列表
            
        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        all_errors = []
        
        # 验证笔的连续性
        is_valid, errors = SegmentValidator.validate_stroke_continuity(strokes)
        all_errors.extend(errors)
        
        # 验证笔的方向交替性
        is_valid, errors = SegmentValidator.validate_stroke_direction_alternation(strokes)
        all_errors.extend(errors)
        
        # 验证线段的连续性
        is_valid, errors = SegmentValidator.validate_segment_continuity(segments)
        all_errors.extend(errors)
        
        # 验证线段的方向交替性
        is_valid, errors = SegmentValidator.validate_segment_direction_alternation(segments)
        all_errors.extend(errors)
        
        # 验证线段构成
        is_valid, errors = SegmentValidator.validate_segment_composition(segments, strokes)
        all_errors.extend(errors)
        
        return len(all_errors) == 0, all_errors