# 批量OCR处理快速开始

## 🎯 当前状态

已处理 2 张图片，还有 20 张待处理。

## 🚀 继续处理剩余图片

### 方法1：使用批量处理脚本（推荐）

```bash
cd 东野圭吾图片测试集
python ../scripts/batch_ocr.py . --batch-size 2 --max-retries 3
```

**参数说明**：
- `--batch-size 2`: 每批处理2张图片，避免服务负载过高
- `--max-retries 3`: 失败时最多重试3次
- 自动跳过已处理的图片

### 方法2：分批手动处理

如果遇到连接问题，可以手动分批处理：

```bash
# 处理第1批（2张）
python scripts/recognize_image.py IMG_20251124_221108.jpg
python scripts/recognize_image.py IMG_20251124_221142.jpg

# 等待几秒，然后处理下一批
python scripts/recognize_image.py IMG_20251124_221212.jpg
python scripts/recognize_image.py IMG_20251124_221219.jpg
```

## 📊 生成汇总报告

处理完成后，生成汇总报告：

```bash
python scripts/generate_summary.py 东野圭吾图片测试集/ocr_results
```

报告会生成：
- `batch_summary.json` - JSON格式
- `batch_summary.md` - Markdown格式（更易读）

## 🔧 遇到连接问题时的处理

### 症状
- 出现 "Not connected" 错误
- 工具调用失败

### 解决方案

1. **减少批次大小**
   ```bash
   python scripts/batch_ocr.py . --batch-size 1
   ```

2. **增加重试次数和延迟**
   ```bash
   python scripts/batch_ocr.py . --batch-size 1 --max-retries 5 --retry-delay 5.0
   ```

3. **等待后重试**
   - 等待30秒到1分钟
   - 重新运行批量处理脚本
   - 已处理的图片会自动跳过

4. **检查MCP服务状态**
   - 重启Cursor
   - 检查MCP服务日志

## 📝 当前已处理的图片

- ✅ IMG_20251124_221134.jpg
- ✅ IMG_20251124_221155.jpg

## 📋 待处理的图片（20张）

- IMG_20251124_220855.jpg
- IMG_20251124_220948.jpg
- IMG_20251124_221108.jpg
- IMG_20251124_221142.jpg
- IMG_20251124_221212.jpg
- IMG_20251124_221219.jpg
- IMG_20251124_221231.jpg
- IMG_20251124_221242.jpg
- IMG_20251124_221246.jpg
- IMG_20251124_221338.jpg
- IMG_20251124_221347.jpg
- IMG_20251124_221402.jpg
- IMG_20251124_221408.jpg
- IMG_20251124_221422.jpg
- IMG_20251124_221503.jpg
- IMG_20251124_221509.jpg
- IMG_20251124_221524.jpg
- IMG_20251124_221538.jpg
- IMG_20251124_221601.jpg
- IMG_20251124_221621.jpg

## 💡 建议的处理流程

1. **首次运行**（测试稳定性）
   ```bash
   python scripts/batch_ocr.py . --batch-size 1 --max-retries 3
   ```

2. **如果稳定**（提高效率）
   ```bash
   python scripts/batch_ocr.py . --batch-size 2 --max-retries 3
   ```

3. **如果遇到问题**（保守策略）
   ```bash
   python scripts/batch_ocr.py . --batch-size 1 --max-retries 5 --retry-delay 5.0
   ```

4. **生成最终报告**
   ```bash
   python scripts/generate_summary.py ocr_results
   ```

## 📖 更多信息

详细文档请查看：
- `scripts/BATCH_OCR_README.md` - 完整使用指南
- `docs/MCP工具掉线修复实施报告.md` - 修复说明

