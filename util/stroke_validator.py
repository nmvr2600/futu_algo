#!/usr/bin/env python3
"""
笔验证器
实现笔的连续性验证逻辑
"""

from typing import List, Tuple
from util.chanlun import Stroke, Fractal, FractalType


class StrokeValidator:
    """笔验证器"""
    
    @staticmethod
    def validate_stroke_continuity(strokes: List[Stroke]) -> Tuple[bool, str]:
        """
        验证笔的连续性
        
        Args:
            strokes: 笔列表
            
        Returns:
            Tuple[bool, str]: (是否连续, 错误信息)
        """
        if len(strokes) < 2:
            return True, "笔数量不足，无需验证连续性"
        
        for i in range(1, len(strokes)):
            prev_stroke = strokes[i-1]
            curr_stroke = strokes[i]
            
            # 1. 检查笔与笔之间是否首尾相连
            if prev_stroke.end_index != curr_stroke.start_index:
                return False, f"笔{i}和笔{i+1}之间不连续: 笔{i}结束索引={prev_stroke.end_index}, 笔{i+1}起始索引={curr_stroke.start_index}"
            
            # 2. 检查相邻笔的方向是否相反
            if prev_stroke.direction == curr_stroke.direction:
                return False, f"笔{i}和笔{i+1}方向相同: 都是{'上涨' if prev_stroke.direction == 1 else '下跌'}笔"
            
            # 3. 检查分型编号是否连续
            if prev_stroke.fractal_end != curr_stroke.fractal_start:
                return False, f"笔{i}和笔{i+1}分型编号不连续: 笔{i}结束分型={prev_stroke.fractal_end}, 笔{i+1}起始分型={curr_stroke.fractal_start}"
        
        return True, "所有笔都满足连续性要求"
    
    @staticmethod
    def validate_stroke_validity(stroke: Stroke, fractals: List[Fractal]) -> Tuple[bool, str]:
        """
        验证单个笔的有效性
        
        Args:
            stroke: 笔对象
            fractals: 分型列表
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        # 检查起始和结束分型是否存在
        start_fractal = None
        end_fractal = None
        
        for fractal in fractals:
            if fractal.idx == stroke.fractal_start:
                start_fractal = fractal
            if fractal.idx == stroke.fractal_end:
                end_fractal = fractal
        
        if start_fractal is None:
            return False, f"找不到起始分型 {stroke.fractal_start}"
        
        if end_fractal is None:
            return False, f"找不到结束分型 {stroke.fractal_end}"
        
        # 检查起始和结束分型类型是否不同
        if start_fractal.type == end_fractal.type:
            return False, f"起始分型和结束分型类型相同: 都是{'顶' if start_fractal.type == FractalType.TOP else '底'}分型"
        
        # 检查方向是否正确
        expected_direction = 1 if end_fractal.type == FractalType.TOP else -1
        if stroke.direction != expected_direction:
            return False, f"笔方向错误: 期望{'上涨' if expected_direction == 1 else '下跌'}, 实际{'上涨' if stroke.direction == 1 else '下跌'}"
        
        return True, "笔有效"
    
    @staticmethod
    def validate_fractal_sequence(fractals: List[Fractal]) -> Tuple[bool, str]:
        """
        验证分型序列的有效性
        
        Args:
            fractals: 分型列表
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if len(fractals) < 2:
            return True, "分型数量不足，无需验证序列有效性"
        
        for i in range(1, len(fractals)):
            prev_fractal = fractals[i-1]
            curr_fractal = fractals[i]
            
            # 1. 检查相邻分型类型是否不同
            if prev_fractal.type == curr_fractal.type:
                return False, f"分型{i}和分型{i+1}类型相同: 都是{'顶' if prev_fractal.type == FractalType.TOP else '底'}分型"
            
            # 2. 检查分型之间是否有足够的间隔
            if curr_fractal.index - prev_fractal.index < 2:
                return False, f"分型{i}和分型{i+1}之间间隔不足: 索引差={curr_fractal.index - prev_fractal.index}"
        
        return True, "分型序列有效"