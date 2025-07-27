# 数据导出工具

## 功能说明

该工具支持从网络下载股票数据并导出为包含MACD指标的CSV文件。导出的CSV文件包含以下字段：

- `time_key`: 时间
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- `MACD_DIFF`: MACD线 (DIF)
- `MACD_DEA`: 信号线 (DEM)
- `MACD_HIST`: 柱状图 (BAR)

## 安装依赖

```bash
pip install yfinance pandas numpy
```

## 使用方法

### 基本用法

```bash
python export_data.py -s "股票代码" -p "数据周期" -o "输出文件路径"
```

### 参数说明

- `-s`, `--symbol`: 股票代码 (如: 0700.HK, AAPL, 000001.SZ)
- `-p`, `--period`: 数据周期 
  - 可选值: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
  - 默认值: 1y
- `-o`, `--output`: 输出CSV文件路径
- `--source`: 数据源 (目前仅支持 yahoo)
- `--fast`: MACD快线周期 (默认12)
- `--slow`: MACD慢线周期 (默认26)
- `--signal`: MACD信号线周期 (默认9)
- `--verbose`, `-v`: 显示详细日志

### 示例

```bash
# 从Yahoo Finance下载腾讯控股数据
python export_data.py -s "0700.HK" -p "1y" -o "tencent_data.csv"

# 从Yahoo Finance下载苹果数据，指定数据周期为3个月
python export_data.py -s "AAPL" -p "3mo" -o "apple_data.csv"

# 从Yahoo Finance下载平安银行数据，自定义MACD参数
python export_data.py -s "000001.SZ" -p "6mo" -o "pingan_data.csv" --fast 10 --slow 20 --signal 5

# 显示详细日志
python export_data.py -s "0700.HK" -p "1mo" -o "tencent_data.csv" --verbose
```

## 支持的股票代码格式

### 港股
- 格式: `XXXX.HK` (如 0700.HK 表示腾讯控股)

### 美股
- 格式: `XXXX` (如 AAPL 表示苹果公司)

### A股
- 格式: `XXXXXX.SZ` 或 `XXXXXX.SH` (如 000001.SZ 表示平安银行)

## 输出文件示例

```csv
time_key,open,high,low,close,volume,MACD_DIFF,MACD_DEA,MACD_HIST
2025-06-25 00:00:00+08:00,512.0,515.0,508.0,512.5,17592461,0.0,0.0,0.0
2025-06-26 00:00:00+08:00,512.0,513.0,507.5,513.0,15000643,0.0398860398860279,0.00797720797720558,0.03190883190882232
2025-06-27 00:00:00+08:00,512.0,514.5,510.0,513.0,15181667,0.07068124447039281,0.02051801527584303,0.05016322919454978
```

## 注意事项

1. 确保网络连接正常，以便从Yahoo Finance获取数据
2. 输出文件路径中的目录会自动创建
3. MACD参数需要满足: 0 < fast < slow, signal > 0
4. 如果股票代码无效或数据不可用，程序会显示错误信息并退出