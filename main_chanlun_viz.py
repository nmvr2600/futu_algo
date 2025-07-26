#!/usr/bin/env python3
"""
缠论可视化主入口
支持命令行参数指定股票代码、周期和K线数量
"""

import argparse
import sys
import os
from datetime import datetime
from chanlun_advanced_visualizer import generate_divergence_chart


def print_banner():
    """打印程序启动横幅"""
    banner = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           缠论技术分析可视化工具                ┃
┃        Chanlun Technical Analysis Visualizer ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """
    print(banner)


def main():
    """主函数 - 处理命令行参数并生成缠论图表"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='缠论技术分析图表生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s 0700.HK                    # 生成腾讯图表，使用默认参数
  %(prog)s 0700.HK -p 1y              # 生成1年数据图表
  %(prog)s 0700.HK -k 500             # 使用最近500根K线
  %(prog)s 0700.HK -p 6mo -k 360      # 生成6个月图表，限制360根K线
  %(prog)s 0005.HK -p 2y -k 720       # 生成汇丰2年图表，限制720根K线
        """
    )
    
    # 添加参数
    parser.add_argument(
        'stock_code',
        help='股票代码 (如: 0700.HK, 0005.HK, AAPL)'
    )
    
    parser.add_argument(
        '-p', '--period',
        default='2y',
        choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        help='数据周期 (默认: 2y)'
    )
    
    parser.add_argument(
        '-k', '--kline_count',
        type=int,
        help='使用K线数量 (如: 360, 500, 720)'
    )
    
    parser.add_argument(
        '-i', '--interval',
        default='1d',
        choices=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
        help='K线周期 (默认: 1d)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./chanlun_reports',
        help='输出目录 (默认: ./chanlun_reports)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    parser.add_argument(
        '--list-examples',
        action='store_true',
        help='显示示例股票代码列表'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    if args.list_examples:
        print("\n常用股票代码示例:")
        examples = {
            "港股": ["0700.HK", "0005.HK", "0941.HK", "2382.HK", "1211.HK"],
            "美股": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
            "中概股": ["BABA", "JD", "PDD", "BILI", "NIO"]
        }
        for market, codes in examples.items():
            print(f"{market}: {', '.join(codes)}")
        return
    
    # 打印参数信息
    if args.verbose:
        print(f"\n运行参数:")
        print(f"股票代码: {args.stock_code}")
        print(f"数据周期: {args.period}")
        print(f"K线间隔: {args.interval}")
        print(f"K线数量: {args.kline_count or '全部'}")
        print(f"输出目录: {args.output}")
        print("-" * 50)
    
    # 生成图表
    try:
        start_time = datetime.now()
        
        if args.verbose:
            print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] 开始生成 {args.stock_code} 的缠论图表...")
        
        chart_path = generate_divergence_chart(
            stock_code=args.stock_code,
            period=args.period,
            interval=args.interval,
            kline_count=args.kline_count,
            save_dir=args.output
        )
        
        if chart_path and os.path.exists(chart_path):
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n✅ 图表生成成功!")
            print(f"📊 股票: {args.stock_code}")
            print(f"📁 路径: {chart_path}")
            print(f"⏱️  耗时: {duration:.2f}秒")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            print(f"❌ 图表生成失败: {args.stock_code}")
            
    except KeyboardInterrupt:
        print("\n😡 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        with open('error.log', 'a') as f:
            f.write(f"[{datetime.now()}] {args.stock_code}: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()