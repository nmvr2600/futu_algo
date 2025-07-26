# 缠论可视化数据结构说明

本文档详细说明了缠论可视化工具在绘图时传入的数据结构，采用基于time_key的简化设计。

## 1. K线数据结构 (df参数)

这是一个Pandas DataFrame，包含以下列：

### 1.1 基本列
- `time_key`: 时间戳（datetime类型），作为K线的唯一标识符
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量（可选）

### 1.2 示例数据
```
         time_key    open    high     low   close
0 2024-01-01 00:00  100.00  101.00   99.00  100.50
1 2024-01-01 00:15  100.50  102.00   99.50  101.50
2 2024-01-01 00:30  101.50  103.00  100.00  102.50
...
```

## 2. 缠论分析结果结构 (result参数)

这是一个字典，包含以下键值对：

### 2.1 分型 (fractals)
分型列表，每个分型包含：
- `time_key`: 关键K线的时间戳（唯一标识符）
- `related_time_keys`: 关联K线的时间戳列表（可选，用于调试）
- `type`: 分型类型（顶分型/底分型）
- `price`: 分型价格
- `idx`: 分型编号（仅用于调试显示，不用于索引引用）

### 2.2 笔 (strokes)
笔列表，每个笔包含：
- `start_time_key`: 起始分型的时间戳
- `end_time_key`: 结束分型的时间戳
- `start_price`: 起始价格
- `end_price`: 结束价格
- `direction`: 方向（1表示上涨，-1表示下跌）
- `idx`: 笔序号（仅用于调试显示）

### 2.3 线段 (segments)
线段列表，每个线段包含：
- `start_time_key`: 起始笔的时间戳标识
- `end_time_key`: 结束笔的时间戳标识
- `start_price`: 起始价格
- `end_price`: 结束价格
- `direction`: 方向（1表示上涨，-1表示下跌）

### 2.4 中枢 (centrals)
中枢列表，每个中枢包含：
- `start_time_key`: 起始笔的时间戳标识
- `end_time_key`: 结束笔的时间戳标识
- `high`: 中枢上沿价格
- `low`: 中枢下沿价格

## 3. 基于time_key的关联机制

### 3.1 设计原则
- 所有层级的元素都使用time_key作为唯一标识和关联依据
- time_key具有全局唯一性，不会存在重复
- 可视化时直接通过time_key在原始K线数据中定位

### 3.2 关联示例
```
K线数据: time_key -> {open, high, low, close}
分型: time_key_F -> K线中的time_key
笔: start_time_key -> 分型的time_key_F1, end_time_key -> 分型的time_key_F2
线段: start_time_key -> 笔的start_time_key1, end_time_key -> 笔的start_time_key2
中枢: start_time_key -> 笔的start_time_key1, end_time_key -> 笔的start_time_key2
```

## 4. 时间数据处理

### 4.1 时间数据结构
- `dates`: datetime格式的时间序列
- `x_dates`: 转换为数字格式的时间序列，用于绘图

### 4.2 时间轴格式化
根据不同时间周期自动调整日期格式：
- 一周内: '%m-%d %H:%M'
- 一个月内: '%m-%d'
- 一年内: '%Y-%m'
- 超过一年: '%Y-%m-%d'

## 5. 数据处理流程

### 5.1 处理步骤
1. **原始数据获取**: 从yfinance或其他数据源获取原始K线数据
2. **缠论分析**: 在原始数据上进行分型、笔、线段、中枢识别
3. **绘图**: 使用原始数据进行绘图，通过time_key直接定位缠论元素

### 5.2 设计原则
- 用户看到的是完整的原始K线数据
- 所有缠论元素通过time_key直接定位到原始K线上
- 移除了复杂的索引映射转换，简化了数据结构

这种设计确保了可视化效果既准确又简洁，避免了索引映射带来的复杂性和潜在bug。