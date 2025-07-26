#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证中枢识别功能合并是否成功
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor
import inspect


def check_central_class():
    """检查Central类是否包含新的属性"""
    print("检查Central类定义...")
    
    # 获取Central类的源代码
    source = inspect.getsource(ChanlunProcessor.build_centrals)
    
    # 检查是否包含新的属性
    has_start_timestamp = "start_timestamp" in source
    has_end_timestamp = "end_timestamp" in source
    has_strokes = "strokes" in source
    
    print(f"- 包含start_timestamp: {has_start_timestamp}")
    print(f"- 包含end_timestamp: {has_end_timestamp}")
    print(f"- 包含strokes: {has_strokes}")
    
    return has_start_timestamp and has_end_timestamp and has_strokes


def check_legacy_file():
    """检查legacy文件是否已被删除"""
    print("\n检查legacy文件是否已被删除...")
    
    legacy_path = "/Users/macyou/workspace-xhs/futu_algo/util/chanlun_legacy.py"
    exists = os.path.exists(legacy_path)
    print(f"- chanlun_legacy.py存在: {exists}")
    
    return not exists


def check_central_method():
    """检查中枢识别方法是否已更新"""
    print("\n检查中枢识别方法...")
    
    # 获取build_centrals方法的源代码
    source = inspect.getsource(ChanlunProcessor.build_centrals)
    
    # 检查是否包含新的中枢识别逻辑
    has_direction_check = "stroke1.direction == stroke3.direction" in source
    has_overlap_calculation = "overlap_high" in source and "overlap_low" in source
    
    print(f"- 包含笔方向检查: {has_direction_check}")
    print(f"- 包含重叠区间计算: {has_overlap_calculation}")
    
    return has_direction_check and has_overlap_calculation


def main():
    print("开始验证中枢识别功能合并...")
    
    # 检查各项内容
    central_class_ok = check_central_class()
    legacy_file_deleted = check_legacy_file()
    central_method_ok = check_central_method()
    
    print(f"\n验证结果:")
    print(f"- Central类定义正确: {central_class_ok}")
    print(f"- Legacy文件已删除: {legacy_file_deleted}")
    print(f"- 中枢识别方法已更新: {central_method_ok}")
    
    all_ok = central_class_ok and legacy_file_deleted and central_method_ok
    print(f"\n总体结果: {'通过' if all_ok else '未通过'}")
    
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)