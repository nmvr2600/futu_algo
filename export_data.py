#!/usr/bin/env python3
"""
数据导出工具
支持从网络下载股票数据并导出为包含MACD指标的CSV文件
"""

import argparse
import sys
import os
import pandas as pd
import numpy as np
import yfinance as yf
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 从项目中导入MACD计算方法
from chanlun_advanced_visualizer import AdvancedChanlunVisualizer

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    计算MACD指标
    
    Args:
        df: 包含股价数据的DataFrame
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期
        
    Returns:
        dict: 包含MACD线、信号线和柱状图的字典
    """
    try:
        # 复用项目中的MACD计算方法
        visualizer = AdvancedChanlunVisualizer()
        return visualizer._calculate_macd(df, fast=fast, slow=slow, signal=signal)
    except Exception as e:
        logger.error(f"计算MACD指标失败: {str(e)}")
        raise


def get_data_from_yahoo(symbol, period="1y"):
    """
    从Yahoo Finance获取股票数据
    
    Args:
        symbol: 股票代码
        period: 数据周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        pandas.DataFrame: 股票数据
    """
    try:
        logger.info(f"从Yahoo Finance获取 {symbol} 的数据，周期: {period}")
        
        # 使用yfinance获取数据
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            raise ValueError(f"无法获取 {symbol} 的数据")
        
        # 重命名列以匹配项目要求的格式
        data = data.reset_index()
        data.rename(columns={
            'Date': 'time_key',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # 确保列的顺序和数据类型正确
        required_columns = ['time_key', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"缺少必要的列: {col}")
        
        logger.info(f"成功获取 {len(data)} 条数据记录")
        return data[required_columns]
    except Exception as e:
        logger.error(f"从Yahoo Finance获取数据失败: {str(e)}")
        raise


def export_to_csv(data, output_file):
    """
    将数据导出为CSV文件
    
    Args:
        data: 包含所有数据的DataFrame
        output_file: 输出文件路径
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
        
        data.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"数据已成功导出到: {output_file}")
    except Exception as e:
        logger.error(f"导出CSV文件失败: {str(e)}")
        raise


def validate_args(args):
    """
    验证命令行参数
    
    Args:
        args: 命令行参数对象
        
    Raises:
        ValueError: 参数验证失败时抛出异常
    """
    # 验证股票代码不为空
    if not args.symbol:
        raise ValueError("股票代码不能为空")
    
    # 验证输出文件路径不为空
    if not args.output:
        raise ValueError("输出文件路径不能为空")
    
    # 验证MACD参数
    if args.fast <= 0:
        raise ValueError("MACD快线周期必须大于0")
    if args.slow <= 0:
        raise ValueError("MACD慢线周期必须大于0")
    if args.signal <= 0:
        raise ValueError("MACD信号线周期必须大于0")
    if args.fast >= args.slow:
        raise ValueError("MACD快线周期必须小于慢线周期")
    
    logger.info("参数验证通过")


def main():
    """主函数"""
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="股票数据导出工具")
    parser.add_argument("-s", "--symbol", type=str, required=True, help="股票代码 (如: 0700.HK, AAPL)")
    parser.add_argument("-p", "--period", type=str, default="1y", 
                       choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                       help="数据周期")
    parser.add_argument("-o", "--output", type=str, required=True, help="输出CSV文件路径")
    parser.add_argument("--source", type=str, default="yahoo", choices=["yahoo"], help="数据源")
    parser.add_argument("--fast", type=int, default=12, help="MACD快线周期")
    parser.add_argument("--slow", type=int, default=26, help="MACD慢线周期")
    parser.add_argument("--signal", type=int, default=9, help="MACD信号线周期")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        logger.info("开始执行数据导出任务")
        logger.debug(f"参数: symbol={args.symbol}, period={args.period}, output={args.output}, "
                    f"source={args.source}, fast={args.fast}, slow={args.slow}, signal={args.signal}")
        
        # 验证参数
        validate_args(args)
        
        print(f"开始获取 {args.symbol} 的数据...")
        
        # 获取数据
        if args.source == "yahoo":
            data = get_data_from_yahoo(args.symbol, args.period)
        else:
            raise ValueError(f"不支持的数据源: {args.source}")
        
        print(f"成功获取 {len(data)} 条数据记录")
        
        # 计算MACD指标
        print("计算MACD指标...")
        logger.info("开始计算MACD指标")
        macd_result = calculate_macd(data, args.fast, args.slow, args.signal)
        
        # 将MACD指标添加到数据中
        data['MACD_DIFF'] = macd_result['macd_line']
        data['MACD_DEA'] = macd_result['signal_line']
        data['MACD_HIST'] = macd_result['histogram']
        
        # 导出为CSV
        print("导出数据到CSV文件...")
        logger.info("开始导出数据到CSV文件")
        export_to_csv(data, args.output)
        
        print("数据导出完成!")
        logger.info("数据导出任务完成")
        
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()