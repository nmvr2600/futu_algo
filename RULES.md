# 缠论量化交易系统 - 开发规范与规则

## 1. 项目概述

本项目是一个基于缠论理论的量化交易系统，使用Python开发，支持多数据源、多时间周期的技术分析和量化交易。

## 2. 技术栈

### 2.1 核心依赖
- **Python**: 3.8+
- **pandas**: 数据处理核心库
- **numpy**: 数值计算
- **matplotlib**: 可视化图表
- **yfinance**: Yahoo Finance数据源
- **tushare**: 国内数据源
- **futu-api**: 富途数据源

### 2.2 开发工具
- **pytest**: 单元测试框架
- **black**: 代码格式化
- **flake8**: 代码质量检查
- **mypy**: 类型检查

## 3. 代码规范

### 3.1 命名规范
- **类名**: PascalCase (如 `ChanlunProcessor`)
- **函数名**: snake_case (如 `build_strokes`)
- **变量名**: snake_case (如 `start_price`)
- **常量**: UPPER_SNAKE_CASE (如 `DEFAULT_WINDOW_SIZE`)

### 3.2 代码风格
- **行长度**: 每行不超过88个字符
- **缩进**: 使用4个空格
- **引号**: 统一使用双引号
- **注释**: 使用中文注释，函数必须有docstring

### 3.3 类型提示
- 所有函数参数和返回值必须添加类型注解
- 使用 `from typing import ...` 引入类型提示

```python
from typing import List, Dict, Optional

def build_strokes(self, df: pd.DataFrame) -> List[Stroke]:
    """构建笔结构"""
    pass
```

## 4. 项目结构规范

### 4.1 目录结构
```
futu_algo/
├── util/           # 工具类和核心算法
├── engines/        # 数据引擎和交易引擎
├── strategies/     # 交易策略
├── filters/        # 数据过滤器
├── tests/          # 测试文件
├── config/         # 配置文件
├── data/           # 数据存储
└── custom/         # 自定义扩展
```

### 4.2 文件命名
- **模块文件**: snake_case.py (如 `chanlun.py`)
- **测试文件**: test_*.py (如 `test_chanlun.py`)
- **配置文件**: *.ini (如 `config.ini`)

## 5. 数据规范

### 5.1 K线数据结构
所有K线数据统一使用pandas DataFrame格式，必须包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| time_key | str | 时间戳，格式'YYYY-MM-DD HH:MM:SS' |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | int | 成交量 |

### 5.2 数据验证
- 数据必须按时间升序排列
- 不得包含缺失值
- 时间间隔必须一致

## 6. 测试规范

### 6.1 TDD开发模式（强制要求）

#### 📌 强制TDD工作流

1. **红阶段（Red Phase）**
   - 必须先在 `/tests/` 目录下编写**失败测试用例**
   - 测试函数必须以 `test_` 开头
   - 使用 `pytest` 框架，确保测试能运行且预期失败

2. **绿阶段（Green Phase）**
   - 仅编写**最小实现**让测试通过
   - 禁止提前优化
   - 禁止跳过测试运行

3. **重构阶段（Refactor Phase）**
   - 在测试全部通过的前提下进行重构
   - 保持测试持续通过
   - 提升代码可读性和性能

#### 🚫 禁止行为
- 直接编写业务逻辑而不先写测试
- 将测试代码混入 `/src` 或 `/util` 目录
- 跳过 `pytest` 测试运行
- 提交未通过测试的代码

#### 🎯 测试覆盖率要求
- **核心算法模块**: 必须达到90%以上
- **数据引擎模块**: 必须达到85%以上
- **策略模块**: 必须达到80%以上
- **工具类模块**: 必须达到85%以上

#### 🧪 测试分类规范
- **单元测试**: `test_*.py` - 测试单个函数或类
- **集成测试**: `integration_*.py` - 测试模块间交互
- **性能测试**: `performance_*.py` - 测试性能指标
- **边界测试**: `edge_*.py` - 测试边界条件

#### 📋 测试命名规范
```python
def test_build_strokes_with_valid_data():
    """测试有效数据下的笔构建"""
    pass

def test_build_strokes_with_empty_data():
    """测试空数据情况"""
    pass

def test_build_strokes_edge_cases():
    """测试边界情况"""
    pass

def test_fractal_identification_with_minimum_klines():
    """测试最少K线数量下的分型识别"""
    pass

def test_central_zone_calculation_overlapping_prices():
    """测试重叠价格区间的中枢计算"""
    pass
```

#### 🧪 测试数据规范
- 使用 `pytest.fixture` 提供测试数据
- 测试数据必须可重复生成
- 避免使用真实市场数据做单元测试
- 为每种边界条件创建独立测试数据

#### 🎯 TDD示例流程
```python
# 步骤1: 先写失败的测试
# tests/test_chanlun.py
def test_merge_klines_with_containment():
    """测试包含关系的K线合并"""
    # 准备测试数据
    df = pd.DataFrame({
        'time_key': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open': [100, 102, 101],
        'high': [105, 104, 103],
        'low': [98, 99, 100],
        'close': [103, 101, 102],
        'volume': [1000, 1200, 1100]
    })
    
    processor = ChanlunProcessor()
    result = processor.merge_klines(df)
    
    # 验证合并结果
    assert len(result) == 2  # 预期合并为2根K线
    assert result.iloc[0]['high'] == 105  # 验证最高价

# 步骤2: 运行测试确认失败
# pytest tests/test_chanlun.py::test_merge_klines_with_containment -v

# 步骤3: 实现最小功能让测试通过
# util/chanlun.py
class ChanlunProcessor:
    def merge_klines(self, df: pd.DataFrame) -> pd.DataFrame:
        """合并包含关系的K线"""
        if len(df) <= 2:
            return df
        
        # 最小实现：简单合并前两根
        merged = df.iloc[:2].copy()
        merged.loc[0, 'high'] = max(df.iloc[0]['high'], df.iloc[1]['high'])
        merged.loc[0, 'low'] = min(df.iloc[0]['low'], df.iloc[1]['low'])
        
        return pd.concat([merged.iloc[:1], df.iloc[2:]])

# 步骤4: 运行测试确认通过
# pytest tests/test_chanlun.py::test_merge_klines_with_containment -v

# 步骤5: 重构优化代码
# 在测试通过的前提下进行代码重构
```

### 6.2 测试工具配置
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=util
    --cov=engines
    --cov=strategies
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=85
```

## 7. 缠论算法规范

### 7.1 分型识别
- **顶分型**: 中间K线高点最高，低点也最高
- **底分型**: 中间K线低点最低，高点也最低
- **编号规则**: 按顺序1,2,3,4...连续编号

### 7.2 笔构建规则
- **最小笔**: 至少包含两个不同方向的分型
- **方向**: 1表示上涨，-1表示下跌
- **索引**: 使用合并后K线索引

### 7.3 线段构建
- **最小线段**: 至少包含3笔
- **方向一致性**: 线段内所有笔方向必须一致
- **连续性**: 必须连续，不能有跳空

### 7.4 中枢识别
- **最小中枢**: 至少3笔重叠区域
- **中枢级别**: 从1开始，支持多级中枢
- **边界计算**: 取重叠区域的最高价和最低价

## 8. 可视化规范

### 8.1 图表配置
- **颜色主题**: 使用config/themes/中的配置文件
- **字体**: 支持中英文显示，优先使用系统字体
- **分辨率**: 默认DPI=100，支持高清输出

### 8.2 元素标注
- **分型**: 使用^表示顶分型，v表示底分型
- **笔**: 用[开始分型,结束分型]格式标注
- **线段**: 用[开始分型,结束分型]格式标注
- **中枢**: 用阴影区域表示，标注价格区间

## 9. 错误处理规范

### 9.1 异常处理
```python
try:
    result = processor.process(df)
except ValueError as e:
    logger.error(f"数据处理错误: {e}")
    raise
except IndexError as e:
    logger.error(f"索引越界: {e}")
    raise
```

### 9.2 边界检查
- 空数据处理
- 单根K线处理
- 数据不足时的处理

## 10. 性能规范

### 10.1 内存管理
- 大数据集使用分块处理
- 及时释放不用的变量
- 使用生成器处理大文件

### 10.2 计算优化
- 向量化计算优先于循环
- 缓存重复计算结果
- 使用NumPy加速数值计算

## 11. 日志规范

### 11.1 日志级别
- **DEBUG**: 详细调试信息
- **INFO**: 关键处理步骤
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 11.2 日志格式
```
[时间] [级别] [模块] [函数] 消息
```

## 12. 配置管理

### 12.1 配置文件
- **全局配置**: config/config_template.ini
- **主题配置**: config/themes/
- **日志配置**: 使用Python标准logging配置

### 12.2 环境变量
- **FUTU_API_KEY**: 富途API密钥
- **TUSHARE_TOKEN**: TuShare令牌
- **DATA_PATH**: 数据存储路径

## 13. 版本管理

### 13.1 Git规范
- **分支命名**: feature/功能描述, bugfix/问题描述
- **提交信息**: 使用中文，格式"类型: 描述"
- **标签管理**: 使用语义化版本号

### 13.2 发布流程
1. 所有测试通过
2. 更新版本号
3. 更新CHANGELOG.md
4. 创建发布标签

## 14. 文档规范

### 14.1 代码文档
- 所有公共函数必须有docstring
- 复杂算法需要详细注释
- 使用类型提示

### 14.2 文档结构
- **README.md**: 项目介绍和快速开始
- **API文档**: 自动生成API文档
- **教程**: docs/tutorial/
- **示例**: examples/

## 15. 安全检查

### 15.1 敏感信息
- 不得提交API密钥到代码库
- 使用环境变量存储敏感信息
- 定期更新依赖包

### 15.2 输入验证
- 验证所有外部输入
- 防止SQL注入
- 防止路径遍历攻击

## 16. 开发流程

### 16.1 开发步骤
1. 创建功能分支
2. 编写测试用例（TDD模式）
3. 实现功能代码
4. 运行测试（必须全部通过）
5. 代码审查
6. 合并到主分支

### 16.2 代码审查检查单
- [ ] 代码符合规范
- [ ] 测试用例完整（TDD流程）
- [ ] 测试覆盖率达标
- [ ] 文档更新
- [ ] 性能测试通过
- [ ] 安全检查通过

## 17. 持续集成

### 17.1 GitHub Actions
- **代码质量检查**: flake8, black, mypy
- **单元测试**: pytest（强制通过）
- **测试覆盖率**: 必须达到最低要求
- **安全扫描**: 依赖包漏洞扫描

### 17.2 自动化测试
- 每次提交触发测试
- 测试失败阻止合并
- 自动生成测试报告
- 覆盖率报告自动上传

## 18. 部署规范

### 18.1 环境要求
- **操作系统**: Ubuntu 20.04+ / macOS 10.15+
- **Python**: 3.8+
- **内存**: 最少4GB
- **存储**: 最少10GB可用空间

### 18.2 部署步骤
1. 创建虚拟环境
2. 安装依赖
3. 运行完整测试套件
4. 配置环境变量
5. 启动服务

## 19. 监控和报警

### 19.1 监控指标
- **数据处理速度**: 每分钟处理K线数量
- **内存使用**: 峰值内存占用
- **错误率**: 处理失败比例
- **测试通过率**: 100%通过要求

### 19.2 报警规则
- 错误率超过5%
- 内存使用超过80%
- 处理时间超过预期
- 测试失败（立即报警）

## 20. 用户支持

### 20.1 问题反馈
- **Bug报告**: 使用GitHub Issues
- **功能请求**: 使用GitHub Discussions
- **技术支持**: 邮件支持

### 20.2 文档更新
- 随代码更新文档
- 定期审查文档准确性
- 提供多语言支持

---

**最后更新**: 2025年1月
**维护者**: 缠论量化交易团队
**TDD规范**: 强制执行，违者代码不得合并