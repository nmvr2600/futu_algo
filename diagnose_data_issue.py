#!/usr/bin/env python3
"""
数据获取诊断工具
帮助用户诊断股票数据获取问题
"""

import sys
import os
from datetime import datetime

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom.chanlun_selector_demo import get_stock_data

def diagnose_stock_data(stock_code):
    """诊断单个股票的数据获取情况"""
    print(f"\n🔍 正在诊断股票代码: {stock_code}")
    print("-" * 50)
    
    try:
        # 尝试获取1个月的数据
        data = get_stock_data(stock_code, period="1mo", interval="1d")
        
        if data.empty:
            print(f"❌ {stock_code}: 获取到空数据")
            print("可能原因:")
            print("  1. 股票代码不存在或已退市")
            print("  2. Yahoo Finance没有该股票的数据")
            print("  3. 网络连接问题")
            return False
        else:
            print(f"✅ {stock_code}: 成功获取数据")
            print(f"📊 数据条数: {len(data)}")
            print(f"📅 时间范围: {data.index.min()} 到 {data.index.max()}")
            print(f"💰 价格范围: {data['low'].min():.2f} - {data['high'].max():.2f}")
            return True
            
    except Exception as e:
        print(f"❌ {stock_code}: 获取数据时出错")
        print(f"错误信息: {e}")
        print("建议:")
        print("  1. 检查股票代码格式是否正确")
        print("  2. 确认网络连接正常")
        print("  3. 尝试使用其他数据源")
        return False

def show_supported_formats():
    """显示支持的股票代码格式"""
    print("\n📋 支持的股票代码格式示例:")
    print("港股: 0700.HK (腾讯), 0005.HK (汇丰), 0941.HK (中国移动)")
    print("美股: AAPL (苹果), MSFT (微软), TSLA (特斯拉), GOOGL (谷歌)")
    print("中概股: BABA (阿里巴巴), JD (京东), PDD (拼多多)")
    print("A股: 000001.SZ (平安银行), 600000.SS (浦发银行)")
    print("")
    print("格式规则:")
    print("- 港股: 4位数字.HK")
    print("- 美股: 直接使用股票代码")
    print("- A股: 6位数字.交易所后缀(.SZ或.SS)")

def main():
    """主函数"""
    print("🔧 缠论数据获取诊断工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # 命令行模式
        stock_codes = sys.argv[1:]
    else:
        # 交互模式
        print("请输入要诊断的股票代码（空格分隔，直接回车使用示例）:")
        user_input = input("> ").strip()
        
        if not user_input:
            stock_codes = ["0700.HK", "0005.HK", "AAPL", "TSLA", "INVALID_CODE"]
            print(f"使用示例股票: {', '.join(stock_codes)}")
        else:
            stock_codes = user_input.split()
    
    print(f"\n开始诊断 {len(stock_codes)} 个股票代码...")
    
    success_count = 0
    for code in stock_codes:
        if diagnose_stock_data(code):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"诊断完成: {success_count}/{len(stock_codes)} 个股票代码有效")
    
    if success_count < len(stock_codes):
        show_supported_formats()

if __name__ == "__main__":
    main()