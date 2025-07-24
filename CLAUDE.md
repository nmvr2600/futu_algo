# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Futu Algo trading framework for algorithmic high-frequency trading in Hong Kong, Chinese and US stock markets. It uses the FutuOpenD API for market data and trading execution.

## Key Components

- **Data Engine**: Handles market data downloading, processing and storage in parquet format
- **Trading Engine**: Manages real-time trading with Futu API integration
- **Backtesting Engine**: Allows strategy backtesting with historical data
- **Stock Filter Engine**: Screens stocks based on technical indicators
- **Email Engine**: Sends stock filtering results to subscribers
- **Strategies**: Trading strategies like MACD_Cross, KDJ_Cross, EMA_Ribbon, RSI_Threshold
- **Filters**: Stock screening filters like Volume_Threshold, Price_Threshold, Triple_Cross, MA_Simple

## Common Development Commands

### Environment Setup
```bash
# Create conda environment
conda env create -f environment.yml

# Update conda environment
conda env update --name futu_trade --file environment.yml --prune

# Alternative pip installation
pip install -r requirements.txt
```

### Data Management
```bash
# Update all K_1M and K_DAY interval historical data
python main_backend.py -u

# Force update all data (CAUTION!)
python main_backend.py -fu

# Update with specific stock list
python main_backend.py --force_update
```

### Trading Execution
```bash
# Execute algorithmic trading with MACD_Cross strategy
python main_backend.py -s MACD_Cross

# Use different time interval
python main_backend.py -s MACD_Cross --time_interval K_DAY

# Include HSI stocks
python main_backend.py -s MACD_Cross --include_hsi --time_interval K_DAY
```

### Stock Filtering
```bash
# Filter stocks with Volume and Price thresholds
python main_backend.py -f Volume_Threshold Price_Threshold -en "MACD_Cross_Technique" -m HK CHINA
```

### Backtesting
```bash
# Run backtesting for a strategy
python main_backend.py -b MACD_Cross
```

### Testing
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_data_engine.py
```

## Code Architecture

1. **Engines** (`engines/`): Core functionality modules
   - `data_engine.py`: Data processing and storage
   - `trading_engine.py`: Real-time trading execution
   - `backtesting_engine.py`: Strategy backtesting
   - `stock_filter_engine.py`: Stock screening
   - `email_engine.py`: Email notifications

2. **Strategies** (`strategies/`): Trading strategies inheriting from `Strategies` base class
   - Implement `buy()` and `sell()` methods
   - Use technical indicators calculated in `parse_data()`

3. **Filters** (`filters/`): Stock screening filters inheriting from `Filters` base class
   - Implement `filter()` method for stock selection criteria

4. **Main Entry Points**:
   - `main_backend.py`: Command-line interface for all operations
   - `main.py`: (Planned) GUI application

## File Structure
- `data/`: Historical market data in parquet format, organized by stock code
- `config/`: Configuration files (copy config_template.ini to config.ini)
- `strategies/`: Trading strategy implementations
- `filters/`: Stock filtering implementations
- `engines/`: Core engine implementations
- `tests/`: Unit tests
- `util/`: Utility functions and global variables

## Key Development Notes

- Data is stored in parquet format for efficient reading/writing
- Strategies use technical indicators calculated from historical data
- Backtesting simulates trades using historical data with commission fees
- Real-time trading subscribes to market data and executes strategies
- Configuration is managed through config.ini (copy from config_template.ini)

## Supported Time Intervals
K_1M, K_3M, K_5M, K_15M, K_30M, K_60M, K_DAY, K_WEEK, K_MON, K_QUARTER, K_YEAR