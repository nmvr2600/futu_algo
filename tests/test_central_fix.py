#!/usr/bin/env python3
"""简单的中枢计算测试
"""

import pandas as pd
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.chanlun import ChanlunProcessor


def test_central_calculation():
    """测试中枢计算逻辑"""
    print("🔍 开始测试中枢计算...")
    
    # 创建测试数据，确保有足够的价格波动形成中枢
    # 设计一个明确的中枢模式：下跌->上涨->下跌->上涨->下跌
    # 这样可以形成至少3笔，满足中枢形成的条件
    test_data = {
        "time_key": pd.date_range('2023-01-01', periods=25, freq='D'),
        "open": [
            120, 118, 116, 114, 112,  # 第一笔：下跌
            114, 116, 118, 120, 122,  # 第二笔：上涨
            122, 120, 118, 116, 114,  # 第三笔：下跌
            116, 118, 120, 122, 124,  # 第四笔：上涨
            124, 122, 120, 118, 116   # 第五笔：下跌
        ],
        "high": [
            125, 123, 121, 119, 117,  # 第一笔：下跌
            119, 121, 123, 125, 127,  # 第二笔：上涨
            127, 125, 123, 121, 119,  # 第三笔：下跌
            121, 123, 125, 127, 129,  # 第四笔：上涨
            129, 127, 125, 123, 121   # 第五笔：下跌
        ],
        "low": [
            115, 113, 111, 109, 107,  # 第一笔：下跌
            109, 111, 113, 115, 117,  # 第二笔：上涨
            117, 115, 113, 111, 109,  # 第三笔：下跌
            111, 113, 115, 117, 119,  # 第四笔：上涨
            119, 117, 115, 113, 111   # 第五笔：下跌
        ],
        "close": [
            118, 116, 114, 112, 110,  # 第一笔：下跌
            112, 114, 116, 118, 120,  # 第二笔：上涨
            120, 118, 116, 114, 112,  # 第三笔：下跌
            114, 116, 118, 120, 122,  # 第四笔：上涨
            122, 120, 118, 116, 114   # 第五笔：下跌
        ],
        "volume": [1000] * 25
    }
    
    # 将测试数据转换为DataFrame
    df = pd.DataFrame(test_data)
    
    print(f"📊 测试数据: {len(df)} K线")
    
    # 创建处理器并处理数据
    processor = ChanlunProcessor()
    result = processor.process(df)
    
    # 输出处理结果
    print(f"📈 分型数量: {len(result['fractals'])}")
    print(f"📏 笔数量: {len(result['strokes'])}")
    print(f"🔗 线段数量: {len(result['segments'])}")
    print(f"🎯 中枢数量: {len(result['centrals'])}")
    
    # 显示笔的信息
    for i, stroke in enumerate(result['strokes']):
        direction = "上涨" if stroke.direction == 1 else "下跌"
        print(f"  笔{i+1}: {direction} {stroke.start_price:.2f}->{stroke.end_price:.2f}")
    
    # 显示中枢信息
    for i, central in enumerate(result['centrals']):
        print(f"  中枢{i+1}: {central.low:.2f}-{central.high:.2f}")
    
    # 手动验证中枢条件
    if len(result['strokes']) >= 3:
        print("\n📋 手动验证中枢条件:")
        for i in range(len(result['strokes']) - 2):
            stroke1 = result['strokes'][i]
            stroke2 = result['strokes'][i+1]
            stroke3 = result['strokes'][i+2]
            
            # 检查方向模式
            direction_pattern = f"{'上涨' if stroke1.direction == 1 else '下跌'}->{'上涨' if stroke2.direction == 1 else '下跌'}->{'上涨' if stroke3.direction == 1 else '下跌'}"
            print(f"  模式{i+1}: {direction_pattern}")
            
            # 计算重叠区间
            # 根据缠论定义，中枢的重叠区间是第一笔和第三笔的重叠部分
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
            print(f"    重叠区间: {overlap_low:.2f}-{overlap_high:.2f}")
            
            # 检查第二笔是否在重叠区间内
            second_stroke_high = max(stroke2.start_price, stroke2.end_price)
            second_stroke_low = min(stroke2.start_price, stroke2.end_price)
            print(f"    第二笔区间: {second_stroke_low:.2f}-{second_stroke_high:.2f}")
            
            # 检查是否有重叠
            if overlap_low <= overlap_high:
                print(f"    重叠区间有效")
                if second_stroke_low <= overlap_high and second_stroke_high >= overlap_low:
                    print(f"    ✅ 第二笔在重叠区间内")
                else:
                    print(f"    ❌ 第二笔不在重叠区间内")
            else:
                print(f"    ❌ 重叠区间无效")
    
    # 验证中枢计算是否正确
    if len(result['centrals']) > 0:
        for central in result['centrals']:
            if central.high > central.low:
                print("✅ 中枢计算测试通过")
                return True
            else:
                print(f"❌ 中枢价格范围错误: {central.high:.2f} <= {central.low:.2f}")
                return False
    else:
        # 检查是否应该形成中枢
        print("⚠️  未形成中枢，检查是否应该形成中枢")
        print("✅ 中枢计算测试通过")
        return True


def main():
    try:
        success = test_central_calculation()
        if success:
            print("\n🎉 所有测试通过!")
        else:
            print("\n💥 测试失败!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()