#!/usr/bin/env python3
"""
测试新的kline_count参数支持的脚本
"""
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chanlun_advanced_visualizer import generate_divergence_chart


def test_kline_count_feature():
    """测试指定K线数量的新功能"""
    
    print("=== 测试指定K线数量的新功能 ===")
    
    try:
        # 测试案例：不同K线数量
        stock_code = "0700.HK"
        
        # 测试指定K线数量
        test_cases = [
            {"kline_count": 50, "description": "短线测试"},
            {"kline_count": 100, "description": "中短线测试"},
            {"kline_count": 200, "description": "中长线测试"},
            {"kline_count": 300, "description": "长线测试"},
        ]
        
        save_dir = "./kline_count_tests"
        
        results = []
        for test_case in test_cases:
            count = test_case["kline_count"]
            desc = test_case["description"]
            
            print(f"\n--- {desc} ({count}根K线) ---")
            
            chart_path = generate_divergence_chart(
                stock_code, 
                kline_count=count,
                save_dir=save_dir
            )
            
            if chart_path:
                results.append({
                    "count": count,
                    "description": desc,
                    "path": chart_path
                })
                print(f"✓ 成功生成: {chart_path}")
            else:
                print(f"✗ 生成失败")
        
        print(f"\n=== 测试总结 ===")
        for result in results:
            print(f"K线[{result['count']:3d}]: {result['description']} -> {os.path.basename(result['path'])}")
        
        return results
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def quick_demo():
    """快速演示不同K线数量的效果"""
    
    print("=== 快速演示不同K线数量的效果 ===")
    
    stock = "0700.HK"
    outputs = []
    
    for cnt in [60, 120, 180]:
        print(f"\n生成 {cnt} 根K线的图表...")
        path = generate_divergence_chart(stock, kline_count=cnt)
        if path:
            outputs.append(path)
            print(f"  → {path}")
    
    return outputs


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 命令行直接调用
        stock = sys.argv[1]
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        
        path = generate_divergence_chart(
            stock, 
            kline_count=count,
            save_dir="./custom_kline_tests"
        )
        
        if path:
            print(f"✓ 生成成功: {path}")
        else:
            print("✗ 生成失败")
    else:
        # 运行预设测试
        test_kline_count_feature()