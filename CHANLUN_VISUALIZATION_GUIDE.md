# 缠论图形可视化工具使用指南

## 简介

本工具提供了完整的缠论图形可视化功能，能够生成包含K线图、分形、笔、中枢的详细分析报告，支持图片、HTML和PDF格式输出。

## 快速开始

### 1. 基础可视化
使用 `chanlun_visualizer.py` 进行基础可视化：

```bash
# 分析单个股票
python3 chanlun_visualizer.py 0700.HK

# 批量分析默认股票列表
python3 chanlun_visualizer.py
```

### 2. 高级可视化
使用 `chanlun_advanced_visualizer.py` 获得更详细的分析报告：

```bash
# 生成单个股票的完整报告
python3 chanlun_advanced_visualizer.py 0700.HK

# 批量生成报告
python3 chanlun_advanced_visualizer.py
```

## 支持的命令行参数

### 基础工具 (chanlun_visualizer.py)
- 参数：股票代码（可选）
- 示例：`python3 chanlun_visualizer.py 0941.HK`

### 高级工具 (chanlun_advanced_visualizer.py)
- 参数：股票代码（可选）
- 示例：`python3 chanlun_advanced_visualizer.py 0005.HK`

## 输出文件说明

### 文件目录结构
```
chanlun_reports/
├── 0700.HK_20250725_084303.png          # 基础图表
├── 0941.HK_20250725_084444_chart.png    # 高级图表
├── 0941.HK_report.html                  # HTML报告
├── 0941.HK_20250725_084444_report.pdf # PDF报告
└── summary_report.json                  # 批量分析汇总
```

### 文件内容
- **PNG图表**：包含K线图、分形标记、笔连线、中枢区间
- **HTML报告**：交互式网页报告，包含详细分析数据
- **PDF报告**：可打印的完整分析报告
- **JSON汇总**：批量分析的数据汇总

## 可视化内容详解

### 1. 图表元素
- **K线图**：红涨绿跌，显示开盘价、收盘价、最高价、最低价
- **分形标记**：
  - 红色倒三角：顶分型
  - 绿色正三角：底分型
  - 带有价格标注
- **笔连线**：
  - 蓝色实线：上升笔
  - 橙色虚线：下降笔
  - 带有方向箭头和价格变化
- **中枢区间**：
  - 紫色半透明矩形
  - 包含中枢编号和价格区间
  - 显示区间幅度

### 2. 技术指标
- **移动平均线**：MA5、MA10、MA20
- **成交量柱状图**：颜色对应K线涨跌
- **价格分布直方图**：显示价格分布情况

## 支持的港股列表

### 热门港股
- `0700.HK` - 腾讯控股
- `0941.HK` - 中国移动
- `0005.HK` - 汇丰控股
- `0992.HK` - 联想集团
- `0016.HK` - 新鸿基地产
- `0388.HK` - 香港交易所
- `0001.HK` - 长和
- `0002.HK` - 中电控股

### 自定义股票
可以直接使用任何港股代码：
```bash
python3 chanlun_advanced_visualizer.py 3690.HK  # 美团
python3 chanlun_advanced_visualizer.py 9988.HK  # 阿里巴巴
```

## 自定义配置

### 修改数据周期
在脚本中修改以下参数：
```python
# 修改数据获取参数
data = get_stock_data(stock_code, period='1y', interval='1d')  # 1年日线数据
data = get_stock_data(stock_code, period='3mo', interval='30m')  # 3个月30分钟线
```

### 修改保存目录
```python
# 修改保存目录
save_dir = './my_reports'  # 自定义目录
```

## 常见问题

### 1. 中文字体问题
如果遇到中文字体显示问题：
```bash
# macOS安装中文字体
brew install font-microsoft-sonoma
```

### 2. 依赖包安装
确保安装了所有必需的包：
```bash
pip install matplotlib pandas numpy
```

### 3. 数据获取失败
检查网络连接，或尝试更换股票代码。

## 示例输出

### 成功运行示例
```
正在生成 0700.HK 的综合报告...
高级图表已保存到: ./chanlun_reports/0700.HK_20250725_084303_chart.png
HTML报告已保存: ./chanlun_reports/0700.HK_report.html
PDF报告已保存: ./chanlun_reports/0700.HK_20250725_084303_report.pdf

=== 0700.HK 综合报告生成完成 ===
分形数量: 26
笔数量: 12
中枢数量: 1

中枢详情:
  中枢1: 472.28 - 542.27 (区间: 69.99)
```

## 批量分析

### 自定义股票列表
创建自定义股票列表文件：
```python
# 在脚本中修改stock_list
stock_list = ['0700.HK', '0941.HK', '0005.HK', '3690.HK', '9988.HK']
```

### 运行批量分析
```bash
python3 chanlun_advanced_visualizer.py
```

## 技术说明

### 缠论算法
- **分形识别**：基于5根K线的顶底分型判断
- **笔构建**：连接相邻的顶底分型，满足最小距离要求
- **中枢识别**：由至少3笔构成的价格重叠区间

### 数据格式
使用Yahoo Finance API获取数据，支持港股、美股、A股等多种市场。

## 联系与支持

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 发送邮件到项目维护者

---

*最后更新：2025年7月25日*