# Custom Extensions

This directory contains custom implementations and extensions to the original futu_algo project.

## Directory Structure

- `strategies/` - Custom trading strategies
- `engines/` - Extended engines or custom engine implementations
- `config/` - Custom configuration files
- `backtesting/` - Custom backtesting implementations and related files

## Naming Convention

Custom files should be prefixed with `custom_` to distinguish them from the original project files.

## Grid Trading Strategy

This project includes a custom implementation of a grid trading strategy with several variants:
- `grid_backtest.py` - Basic grid trading strategy implementation
- `simple_grid_backtest.py` - Simplified version of the grid strategy
- `grid_backtest_improved.py` - Improved version with optimizations
- `grid_backtest_realistic.py` - More realistic implementation considering trading costs
- `grid_backtest_optimized.py` - Performance-optimized version

Related files:
- `analyze_grid_price.py` - Price analysis tools for grid strategies
- `check_stock_price.py` - Tool for checking stock price data
- `test_grid_strategy.py` - Unit tests for grid trading strategies
- `test_price_format.py` - Test for price formatting in grid strategies
- `GRID_BACKTEST_SUMMARY.md` - Summary of backtesting results
- `GRID_STRATEGY_IMPROVEMENTS.md` - Documented improvements to the strategy