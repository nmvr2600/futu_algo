#!/usr/bin/env python3
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chanlun_advanced_visualizer import generate_divergence_chart


def main():
    # 生成图表
    chart_path = generate_divergence_chart(
        "0700.HK", period="2y", interval="1d", save_dir="./chanlun_reports"
    )
    print(f"生成的图表路径: {chart_path}")


if __name__ == "__main__":
    main()
