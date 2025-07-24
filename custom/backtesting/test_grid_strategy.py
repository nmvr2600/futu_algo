import pandas as pd
import numpy as np
from strategies.Grid_Trading import GridTrading

# 创建模拟数据进行测试
def create_test_data():
    # 生成时间序列
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    
    # 生成价格数据，模拟网格交易场景
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    # 创建DataFrame
    data = pd.DataFrame({
        'code': ['HK.00001'] * 100,
        'time_key': dates,
        'open': prices,
        'close': prices,
        'high': prices + np.abs(np.random.randn(100) * 0.2),
        'low': prices - np.abs(np.random.randn(100) * 0.2),
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    return data

def test_grid_strategy():
    # 创建测试数据
    test_data = create_test_data()
    
    # 初始化输入数据字典
    input_data = {'HK.00001': test_data.copy()}
    
    # 创建网格策略实例
    strategy = GridTrading(input_data, grid_levels=10, grid_spacing=0.02, base_price=100.0)
    
    # 测试策略的基本功能
    print("网格策略测试开始...")
    print(f"基准价格: {strategy.base_price}")
    
    # 测试buy和sell方法
    buy_signals = 0
    sell_signals = 0
    
    for i in range(10, len(test_data)):  # 从第10个数据点开始测试
        # 更新数据
        latest_record = test_data.iloc[[i]]  # 使用双括号保持DataFrame结构
        strategy.parse_data(latest_data=latest_record)
        
        # 检查买卖信号
        if strategy.buy('HK.00001'):
            buy_signals += 1
            print(f"买入信号: {latest_record['time_key'].iloc[0]}, 价格: {latest_record['close'].iloc[0]}")
            
        if strategy.sell('HK.00001'):
            sell_signals += 1
            print(f"卖出信号: {latest_record['time_key'].iloc[0]}, 价格: {latest_record['close'].iloc[0]}")
    
    print(f"\n测试结果:")
    print(f"总买入信号数: {buy_signals}")
    print(f"总卖出信号数: {sell_signals}")
    print(f"最终持仓: {strategy.positions['HK.00001']}")

if __name__ == "__main__":
    test_grid_strategy()