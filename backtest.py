
from datetime import date
from engines.backtesting_engine import BacktestingEngine
from strategies.MACD_Cross import MACDCross

if __name__ == '__main__':
    # 1. Define backtesting parameters
    stock_list = ['HK.00700', 'HK.09988']
    start_date = date(2022, 4, 11)
    end_date = date(2022, 4, 14)

    # 2. Initialize Backtesting Engine
    backtesting_engine = BacktestingEngine(stock_list, start_date, end_date)

    # 3. Prepare data
    backtesting_engine.prepare_input_data_file_1M()

    # 4. Initialize and set strategy
    initial_data = backtesting_engine.get_backtesting_init_data()
    strategy = MACDCross(
        input_data=initial_data,
        fast_period=12,
        slow_period=26,
        signal_period=9
    )
    backtesting_engine.init_strategy(strategy)

    # 5. Run backtesting
    backtesting_engine.calculate_return()

    print("Backtesting finished. Please check the backtesting_report folder for results.")
