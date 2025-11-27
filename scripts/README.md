# Scripts 使用指南

> **脚本目录**: `scripts/`  
> **脚本总数**: 7个脚本 + 1个运行器

## 🚀 快速开始

### 一键运行所有脚本

使用统一脚本运行器 `run_all.py`：

```bash
# 列出所有脚本
python scripts/run_all.py

# 运行所有脚本（跳过需要参数的）
python scripts/run_all.py --all

# 运行指定类别的脚本
python scripts/run_all.py --category config      # 配置类
python scripts/run_all.py --category verification # 验证类
python scripts/run_all.py --category tools       # 工具类

# 运行指定脚本
python scripts/run_all.py --script list_tools

# 交互式选择
python scripts/run_all.py --interactive
```

---

## 📚 脚本分类

### 🔧 配置管理

#### `setup_cursor.py`
自动添加OCR MCP服务到Cursor配置。

**用法**:
```bash
# 添加到Cursor配置
python scripts/setup_cursor.py

# 强制覆盖现有配置
python scripts/setup_cursor.py --force

# 指定服务名称
python scripts/setup_cursor.py --name my-ocr-service
```

#### `check_mcp_config.py`
检查MCP配置文件格式和内容。

**用法**:
```bash
# 检查默认配置文件
python scripts/check_mcp_config.py

# 检查指定配置文件
python scripts/check_mcp_config.py path/to/config.json
```

---

### 🔍 验证脚本

> **注意**: 这些是手动验证/调试脚本，不是pytest单元测试。
> pytest单元测试位于 `tests/` 目录下，使用 `pytest tests/` 运行。

#### `verify_engines.py`
OCR引擎综合验证脚本，全面验证所有功能。

**用法**:
```bash
# 运行所有验证
python scripts/verify_engines.py

# 验证指定引擎
python scripts/verify_engines.py --engine paddleocr

# 使用指定图片验证
python scripts/verify_engines.py --image path/to/image.jpg
```

**验证内容**:
- 模块导入验证
- MCP工具注册验证
- 引擎可用性验证
- OCR识别验证

#### `compare_engines.py`
多引擎对比验证脚本，使用同一张图片对比多个引擎的性能。

**用法**:
```bash
python scripts/compare_engines.py
```

**输出**:
- 性能对比表格
- 详细识别结果
- 最快/最高置信度/最长文本统计

#### `verify_logging.py`
日志系统验证脚本，详细验证日志功能。

**用法**:
```bash
python scripts/verify_logging.py
```

**功能**:
- 初始化日志系统
- 写入测试日志
- 检查日志文件
- 显示日志内容

---

### 🛠️ 工具脚本

#### `list_tools.py`
列出所有OCR MCP工具及其状态。

**用法**:
```bash
python scripts/list_tools.py
```

**输出**:
- 工具名称
- 引擎类型
- 安装状态
- 工具描述
- 参数信息

#### `recognize_image.py`
命令行OCR识别工具。

**用法**:
```bash
# 基本用法
python scripts/recognize_image.py image.jpg

# 指定引擎
python scripts/recognize_image.py image.jpg --engine paddleocr

# JSON输出
python scripts/recognize_image.py image.jpg --json

# 禁用技术分析
python scripts/recognize_image.py image.jpg --no-analysis
```

**支持的引擎**:
- `paddleocr` (默认)
- `paddleocr_mcp`
- `deepseek`

---

## 📋 快速参考

### 使用统一运行器

| 操作 | 命令 |
|------|------|
| 列出所有脚本 | `python scripts/run_all.py` |
| 运行所有脚本 | `python scripts/run_all.py --all` |
| 运行配置类 | `python scripts/run_all.py --category config` |
| 运行验证类 | `python scripts/run_all.py --category verification` |
| 运行工具类 | `python scripts/run_all.py --category tools` |
| 运行指定脚本 | `python scripts/run_all.py --script list_tools` |
| 交互式选择 | `python scripts/run_all.py --interactive` |

### 直接运行单个脚本

| 脚本 | 用途 | 常用命令 |
|------|------|----------|
| `setup_cursor.py` | 配置Cursor | `python scripts/setup_cursor.py` |
| `check_mcp_config.py` | 检查配置 | `python scripts/check_mcp_config.py` |
| `verify_engines.py` | 验证引擎 | `python scripts/verify_engines.py` |
| `compare_engines.py` | 对比引擎 | `python scripts/compare_engines.py` |
| `verify_logging.py` | 验证日志 | `python scripts/verify_logging.py` |
| `list_tools.py` | 列出工具 | `python scripts/list_tools.py` |
| `recognize_image.py` | OCR识别 | `python scripts/recognize_image.py image.jpg` |
| `run_all.py` | 统一运行器 | `python scripts/run_all.py --all` |

---

## 🔍 脚本依赖

所有脚本都需要：
1. Python 3.10+
2. 项目源代码在 `src/` 目录
3. 相应的OCR引擎已安装（根据使用情况）

---

## 💡 使用建议

1. **首次使用**: 先运行 `setup_cursor.py` 配置Cursor
2. **验证安装**: 运行 `verify_engines.py` 验证所有引擎
3. **快速识别**: 使用 `recognize_image.py` 进行OCR识别
4. **查看工具**: 运行 `list_tools.py` 查看可用工具

## 📝 关于测试

- **pytest单元测试**: 位于 `tests/` 目录，使用 `pytest tests/` 运行
- **验证脚本**: 位于 `scripts/` 目录，用于手动验证和调试
- **区别**: 
  - `tests/` = 自动化测试（CI/CD）
  - `scripts/` = 手动验证工具（调试）

---

**最后更新**: 2025-11-27

