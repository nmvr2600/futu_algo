import pandas as pd
import sys
import os
from datetime import date, datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies.Grid_Trading_Improved import GridTradingImproved
from engines.backtesting_engine import BacktestingEngine

def run_improved_grid_backtest():
    # Set up backtesting parameters
    start_date = date(2024, 1, 1)
    end_date = date(2025, 7, 23)
    stock_list = ['HK.03033']  # Southern Hang Seng Tech ETF
    
    # Initialize backtesting engine
    bt = BacktestingEngine(stock_list=stock_list, start_date=start_date, end_date=end_date, observation=100)
    
    # Prepare data for backtesting
    print("Preparing data for backtesting...")
    bt.prepare_input_data_file_1M()  # Using 1M data
    
    # Initialize improved grid trading strategy with better parameters
    print("Initializing improved grid trading strategy...")
    # Use smaller grid spacing (2% instead of 5%) and more levels for better sensitivity
    strategy = GridTradingImproved(bt.get_backtesting_init_data(), grid_levels=20, grid_spacing=0.02, base_price=5.64)
    
    # Set up the strategy in the backtesting engine
    bt.init_strategy(strategy)
    
    # Run backtesting
    print("Running improved grid backtesting...")
    bt.calculate_return()
    
    # Generate HTML report
    print("Generating HTML report...")
    try:
        bt.create_html_report()
    except Exception as e:
        print(f"Error generating HTML report: {e}")
    
    print("Improved grid backtesting completed. Reports have been generated in the backtesting_report directory.")

if __name__ == "__main__":
    run_improved_grid_backtest()