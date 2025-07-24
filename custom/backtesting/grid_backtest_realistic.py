import pandas as pd
import sys
import os
from datetime import date, datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies.Grid_Trading_Realistic import GridTradingRealistic
from engines.backtesting_engine import BacktestingEngine

def run_realistic_grid_backtest():
    # Set up backtesting parameters
    start_date = date(2024, 1, 1)
    end_date = date(2025, 7, 23)
    stock_list = ['HK.03033']  # Southern Hang Seng Tech ETF
    
    # Initialize backtesting engine
    bt = BacktestingEngine(stock_list=stock_list, start_date=start_date, end_date=end_date, observation=100)
    
    # Prepare data for backtesting
    print("Preparing data for backtesting...")
    bt.prepare_input_data_file_1M()  # Using 1M data
    
    # Initialize realistic grid trading strategy with better parameters
    print("Initializing realistic grid trading strategy...")
    # Use 3% grid spacing to ensure sufficient profit to cover transaction costs
    strategy = GridTradingRealistic(bt.get_backtesting_init_data(), grid_levels=10, grid_spacing=0.03, base_price=5.64)
    
    # Set up the strategy in the backtesting engine
    bt.init_strategy(strategy)
    
    # Run backtesting
    print("Running realistic grid backtesting...")
    bt.calculate_return()
    
    # Generate HTML report
    print("Generating HTML report...")
    try:
        bt.create_html_report()
    except Exception as e:
        print(f"Error generating HTML report: {e}")
    
    # Print strategy statistics
    if hasattr(strategy, 'total_pnl') and hasattr(strategy, 'trade_count'):
        for stock_code in stock_list:
            pnl = strategy.total_pnl.get(stock_code, 0)
            count = strategy.trade_count.get(stock_code, 0)
            print(f"Stock {stock_code}: {count} trades, Total PnL: {pnl:.2f} HKD")
    
    print("Realistic grid backtesting completed. Reports have been generated in the backtesting_report directory.")

if __name__ == "__main__":
    run_realistic_grid_backtest()