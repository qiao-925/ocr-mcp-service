# 批量OCR处理脚本使用指南

## 📋 概述

批量OCR处理脚本 (`batch_ocr.py`) 提供了健壮的批量图片OCR处理功能，包含：

- ✅ **自动重试机制** - 处理连接错误和临时故障
- ✅ **分批处理** - 避免服务负载过高
- ✅ **断点续传** - 自动跳过已处理的图片
- ✅ **详细报告** - 生成处理统计和错误列表
- ✅ **进度跟踪** - 实时显示处理进度

## 🚀 快速开始

### 基本用法

```bash
# 处理当前目录的所有图片，每批2张
python scripts/batch_ocr.py .

# 处理指定目录
python scripts/batch_ocr.py /path/to/images

# 指定输出目录
python scripts/batch_ocr.py . --output-dir ./my_results
```

### 高级用法

```bash
# 每批处理3张图片，最多重试5次
python scripts/batch_ocr.py . --batch-size 3 --max-retries 5

# 使用easyocr引擎
python scripts/batch_ocr.py . --engine easyocr

# 不跳过已处理的图片（重新处理所有图片）
python scripts/batch_ocr.py . --no-skip-existing

# 自定义重试延迟（连接错误时等待更长时间）
python scripts/batch_ocr.py . --retry-delay 5.0
```

## 📖 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `image_dir` | 图片目录路径（必需） | - |
| `--output-dir` | 输出目录 | `image_dir/ocr_results` |
| `--engine` | OCR引擎（paddleocr/easyocr/deepseek/paddleocr_mcp） | `paddleocr` |
| `--batch-size` | 每批处理的图片数量 | `2` |
| `--max-retries` | 最大重试次数 | `3` |
| `--retry-delay` | 重试延迟（秒） | `2.0` |
| `--no-skip-existing` | 不跳过已处理的图片 | `False` |
| `--lang` | 语言代码（仅paddleocr） | `ch` |

## 🔄 重试机制

脚本会自动处理以下错误并重试：

- **连接错误** - "Not connected", "Connection" 相关错误
- **超时错误** - TimeoutError
- **临时故障** - 其他可恢复的错误

重试策略：
- 连接错误：等待时间递增（2秒、4秒、6秒...）
- 其他错误：固定延迟（默认2秒）
- 达到最大重试次数后，记录错误并继续处理下一张

## 📊 输出文件

处理完成后，会在输出目录生成：

- `{image_name}_ocr.json` - JSON格式的完整OCR结果
- `{image_name}_ocr.txt` - 纯文本格式的识别结果
- `batch_report.json` - 处理统计报告

## 📈 生成汇总报告

使用 `generate_summary.py` 生成汇总报告：

```bash
# 从ocr_results目录生成汇总报告
python scripts/generate_summary.py ocr_results

# 指定结果目录
python scripts/generate_summary.py /path/to/results

# 指定输出文件
python scripts/generate_summary.py ocr_results --output summary.json
```

汇总报告包含：
- 统计信息（总数、总文本长度、平均置信度等）
- 每张图片的详细信息
- JSON和Markdown两种格式

## 💡 使用建议

### 1. 分批处理大小

- **小图片（< 1MB）**: `--batch-size 3-5`
- **中等图片（1-5MB）**: `--batch-size 2-3`
- **大图片（> 5MB）**: `--batch-size 1-2`

### 2. 重试设置

- **网络不稳定**: `--max-retries 5 --retry-delay 3.0`
- **服务负载高**: `--max-retries 3 --retry-delay 5.0`
- **稳定环境**: `--max-retries 2 --retry-delay 1.0`

### 3. 处理大量图片

```bash
# 分批处理，每批2张，避免服务过载
python scripts/batch_ocr.py . --batch-size 2

# 如果遇到连接问题，增加重试次数和延迟
python scripts/batch_ocr.py . --batch-size 2 --max-retries 5 --retry-delay 3.0
```

## 🔍 故障排查

### 问题：连接错误频繁

**解决方案**：
1. 增加批次间等待时间（修改脚本中的 `wait_time`）
2. 减少批次大小：`--batch-size 1`
3. 增加重试延迟：`--retry-delay 5.0`

### 问题：处理速度慢

**解决方案**：
1. 增加批次大小：`--batch-size 3-5`
2. 使用更快的引擎（paddleocr > easyocr > deepseek）
3. 检查系统资源（CPU、内存）

### 问题：部分图片处理失败

**解决方案**：
1. 检查失败列表（在 `batch_report.json` 中）
2. 单独处理失败的图片
3. 检查图片格式和大小

## 📝 示例

### 示例1：处理测试集

```bash
cd 东野圭吾图片测试集
python ../scripts/batch_ocr.py . --batch-size 2 --max-retries 3
```

### 示例2：重新处理失败的图片

```bash
# 先查看失败列表
cat ocr_results/batch_report.json | grep -A 5 "errors"

# 手动处理失败的图片
python scripts/recognize_image.py failed_image.jpg
```

### 示例3：生成汇总报告

```bash
# 处理完成后生成汇总
python scripts/generate_summary.py 东野圭吾图片测试集/ocr_results
```

## 🎯 最佳实践

1. **首次处理**：使用较小的批次大小（2-3张），观察服务稳定性
2. **稳定后**：可以适当增加批次大小以提高效率
3. **遇到问题**：减少批次大小，增加重试次数
4. **定期检查**：查看 `batch_report.json` 了解处理情况
5. **生成报告**：处理完成后生成汇总报告，便于分析

## 📞 支持

如果遇到问题：
1. 查看 `batch_report.json` 中的错误列表
2. 检查日志文件 `logs/ocr_service.log`
3. 尝试单独处理失败的图片
4. 检查MCP服务连接状态

