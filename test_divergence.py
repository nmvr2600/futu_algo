import pandas as pd
import numpy as np
from chanlun_advanced_visualizer import AdvancedChanlunVisualizer
from util.chanlun import ChanlunProcessor

def create_divergence_test_data():
    """创建具有明显背驰形态的测试数据"""
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    
    # 创建具有明显顶背驰的数据（价格创新高，但MACD柱状图面积减小）
    data = {
        'time_key': dates,
        'open': [50, 51, 52, 53, 54, 53, 52, 51, 52, 53,  # 上涨
                 54, 55, 56, 57, 58, 57, 56, 55, 56, 57,  # 继续上涨（更高）
                 58, 59, 60, 59, 58, 57, 56, 55, 54, 53,  # 下跌
                 52, 51, 50, 49, 48, 49, 50, 51, 52, 53,  # 继续下跌（更低）
                 54, 55, 56, 57, 58, 57, 56, 55, 54, 53], # 反弹
        'high': [52, 53, 54, 55, 56, 55, 54, 53, 54, 55,
                 56, 57, 58, 59, 60, 59, 58, 57, 58, 59,
                 60, 61, 62, 61, 60, 59, 58, 57, 56, 55,
                 54, 53, 52, 51, 50, 51, 52, 53, 54, 55,
                 56, 57, 58, 59, 60, 59, 58, 57, 56, 55],
        'low': [48, 49, 50, 51, 52, 51, 50, 49, 50, 51,
                52, 53, 54, 55, 56, 55, 54, 53, 54, 55,
                56, 57, 58, 57, 56, 55, 54, 53, 52, 51,
                50, 49, 48, 47, 46, 47, 48, 49, 50, 51,
                52, 53, 54, 55, 56, 55, 54, 53, 52, 51],
        'close': [51, 52, 53, 54, 55, 54, 53, 52, 53, 54,
                  55, 56, 57, 58, 59, 58, 57, 56, 57, 58,
                  59, 60, 61, 60, 59, 58, 57, 56, 55, 54,
                  53, 52, 51, 50, 49, 50, 51, 52, 53, 54,
                  55, 56, 57, 58, 59, 58, 57, 56, 55, 54],
        'volume': [1000000] * 50
    }
    
    df = pd.DataFrame(data)
    return df

def test_divergence_detection():
    """测试背驰识别功能"""
    print("测试背驰识别功能")
    
    # 创建测试数据
    df = create_divergence_test_data()
    
    # 缠论分析
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    # 创建可视化器
    visualizer = AdvancedChanlunVisualizer()
    
    # 计算MACD
    macd_result = visualizer._calculate_macd(df)
    
    # 创建索引映射
    index_map = visualizer._create_index_map(df)
    merged_index_map = visualizer._create_merged_index_map(result)
    
    # 识别背驰
    divergences = visualizer._identify_divergences(
        df, result, macd_result, index_map, merged_index_map
    )
    
    print(f"识别到 {len(divergences)} 个背驰信号")
    for div in divergences:
        print(f"  {div['type']}: 价格={div['price']:.2f}, MACD值={div['macd_value']:.4f}")
        if 'macd_area' in div:
            print(f"    MACD红柱面积={div['macd_area']['red']:.4f}, 绿柱面积={div['macd_area']['green']:.4f}")

if __name__ == "__main__":
    test_divergence_detection()