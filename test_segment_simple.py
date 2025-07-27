#!/usr/bin/env python3
"""
简化版线段构建测试 - 专门验证死循环修复
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.chanlun import ChanlunProcessor


def create_minimal_test_data():
    """创建最小测试数据"""
    # 创建足够生成3笔的数据
    dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
    
    # 模拟简单趋势：上涨-下跌-上涨
    prices = [100, 105, 103, 108, 105, 110, 108, 115, 112, 118]
    
    df = pd.DataFrame({
        'time_key': dates,
        'open': prices,
        'high': [p + 1 for p in prices],
        'low': [p - 1 for p in prices],
        'close': prices
    })
    
    return df


def test_segment_building_no_deadlock():
    """测试线段构建无死循环"""
    print("=== 测试线段构建死循环修复 ===")
    
    # 创建最小测试数据
    df = create_minimal_test_data()
    print(f"测试数据: {len(df)} 根K线")
    
    # 设置超时保护
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("线段构建超时 - 死循环未修复")
    
    # 设置5秒超时
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)
    
    try:
        # 创建处理器并运行
        processor = ChanlunProcessor()
        result = processor.process(df)
        
        # 取消超时
        signal.alarm(0)
        
        print(f"✅ 线段构建正常完成")
        print(f"分型数量: {len(processor.fractals)}")
        print(f"笔数量: {len(processor.strokes)}")
        print(f"线段数量: {len(processor.segments)}")
        
        if processor.segments:
            print("\n线段详情:")
            for i, seg in enumerate(processor.segments):
                direction = "上涨" if seg.direction == 1 else "下跌"
                print(f"  线段{i+1}: {direction} {seg.start_price:.2f}->{seg.end_price:.2f}")
        
        return True
        
    except TimeoutError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False


if __name__ == "__main__":
    success = test_segment_building_no_deadlock()
    if success:
        print("\n🎉 死循环问题已修复！")
    else:
        print("\n💥 死循环问题仍存在")