#!/usr/bin/env python3
"""
线段连续性修复验证脚本
用于验证chanlun.py中线段构建算法的连续性修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from util.chanlun import ChanlunProcessor
import yfinance as yf
from datetime import datetime

def verify_segment_continuity():
    """验证线段连续性修复效果"""
    print("🔍 线段连续性修复验证")
    print("=" * 50)
    
    # 使用AAPL真实数据验证
    try:
        # 获取AAPL最近3个月的数据
        ticker = yf.Ticker("AAPL")
        df = ticker.history(period="3mo", interval="1d")
        
        if df.empty:
            print("❌ 无法获取AAPL数据")
            return False
            
        # 准备数据格式
        df.reset_index(inplace=True)
        df['time_key'] = df['Date'].dt.strftime('%Y-%m-%d')
        df = df[['time_key', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['time_key', 'open', 'high', 'low', 'close', 'volume']
        
        print(f"📊 获取数据: {len(df)} 根K线")
        
        # 使用缠论处理器
        processor = ChanlunProcessor()
        result = processor.process(df)
        
        if not result:
            print("❌ 处理失败")
            return False
            
        segments = result.get('segments', [])
        strokes = result.get('strokes', [])
        
        print(f"✅ 处理完成:")
        print(f"   笔数量: {len(strokes)}")
        print(f"   线段数量: {len(segments)}")
        
        # 验证连续性 - 简化验证，确认没有空白
        continuity_ok = True
        
        if len(segments) > 1:
            print("\n🔍 验证线段连续性:")
            
            # 检查是否有空白区域
            all_covered_indices = set()
            for segment in segments:
                for i in range(segment.start_index, segment.end_index + 1):
                    all_covered_indices.add(i)
            
            # 获取所有笔的索引范围
            all_stroke_indices = set()
            for stroke in strokes:
                for i in range(stroke.start_index, stroke.end_index + 1):
                    all_stroke_indices.add(i)
            
            missing_indices = all_stroke_indices - all_covered_indices
            if missing_indices:
                print(f"❌ 发现空白区域: {sorted(missing_indices)}")
                continuity_ok = False
            else:
                print("✅ 所有K线都被线段覆盖，无空白区域")
                
        else:
            print("✅ 只有1个线段，自然连续")
            
        # 验证覆盖完整性
        if strokes and segments:
            first_stroke_start = min(s.start_index for s in strokes)
            last_stroke_end = max(s.end_index for s in strokes)
            
            first_segment_start = min(s.start_index for s in segments)
            last_segment_end = max(s.end_index for s in segments)
            
            if first_segment_start <= first_stroke_start and last_segment_end >= last_stroke_end:
                print("✅ 线段完全覆盖所有笔")
            else:
                print("⚠️  线段覆盖不完整")
                print(f"   笔范围: {first_stroke_start}-{last_stroke_end}")
                print(f"   线段范围: {first_segment_start}-{last_segment_end}")
                
        print("\n🎉 验证完成！")
        return continuity_ok
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    success = verify_segment_continuity()
    if success:
        print("\n✅ 线段连续性修复验证通过！")
    else:
        print("\n❌ 线段连续性验证失败！")