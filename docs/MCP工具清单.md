# MCP 工具清单

本文档列出了 OCR MCP Service 提供的所有可用工具。

## 📋 工具总览

| 工具名称 | 类型 | 功能 | 参数 |
|---------|------|------|------|
| `recognize_image_paddleocr` | OCR识别 | PaddleOCR引擎识别（推荐中文） | `image_path`, `lang="ch"` |
| `recognize_image_easyocr` | OCR识别 | EasyOCR引擎识别（支持80+语言） | `image_path`, `languages="ch_sim,en"` |
| `recognize_image_paddleocr_mcp` | OCR识别 | paddleocr-mcp引擎识别 | `image_path` |
| `recognize_image_deepseek` | OCR识别 | DeepSeek OCR引擎识别（不推荐） | `image_path` |
| `get_prompt_template` | 辅助工具 | 获取通用Prompt模板 | 无 |
| `get_usage_guide` | 辅助工具 | 获取使用指南 | 无 |

---

## 🔍 详细说明

### OCR识别工具

#### 1. `recognize_image_paddleocr`

**功能**：使用 PaddleOCR 引擎识别图片中的文字

**参数**：
- `image_path` (str, 必需): 图片文件路径
- `lang` (str, 可选): 语言代码，默认为 `"ch"`（中文）

**返回**：
```python
{
    "text": "识别的文本内容",
    "boxes": [{"x1": 0, "y1": 0, "x2": 100, "y2": 50}, ...],
    "confidence": 0.95,
    "engine": "paddleocr",
    "processing_time": 1.23,
    "analysis": "技术分析（可选）"
}
```

**适用场景**：
- ✅ 中文文档识别（推荐）
- ✅ 中文图片文字提取
- ✅ 中文表格、图表识别

---

#### 2. `recognize_image_easyocr`

**功能**：使用 EasyOCR 引擎识别图片中的文字，支持80+语言

**参数**：
- `image_path` (str, 必需): 图片文件路径
- `languages` (str, 可选): 逗号分隔的语言代码，默认为 `"ch_sim,en"`（简体中文和英文）

**常用语言代码**：
- `en` - 英文
- `ch_sim` - 简体中文
- `ch_tra` - 繁体中文
- `ja` - 日文
- `ko` - 韩文
- `fr` - 法文
- `de` - 德文

**返回**：同 `recognize_image_paddleocr`

**适用场景**：
- ✅ 多语言文档识别
- ✅ 国际化内容处理
- ✅ 混合语言图片

---

#### 3. `recognize_image_paddleocr_mcp`

**功能**：使用 paddleocr-mcp 引擎识别图片中的文字（官方 MCP 实现）

**参数**：
- `image_path` (str, 必需): 图片文件路径

**返回**：同 `recognize_image_paddleocr`

**适用场景**：
- ✅ 使用官方 MCP 实现
- ✅ 需要标准化的 MCP 接口

---

#### 4. `recognize_image_deepseek`

**功能**：使用 DeepSeek OCR 引擎识别图片中的文字

**参数**：
- `image_path` (str, 必需): 图片文件路径

**返回**：同 `recognize_image_paddleocr`

**⚠️ 注意**：
- ❌ **不推荐使用**：模型较大（~7.8GB）
- ❌ 初始化时间长
- ❌ 资源消耗高

**适用场景**：
- ⚠️ 仅在高准确率需求且资源充足时使用

---

### 辅助工具

#### 5. `get_prompt_template`

**功能**：获取图片分析的通用 Prompt 模板示例

**参数**：无

**返回**：
```python
{
    "template": "请分析这张图片：\n\n**第一步：OCR 识别**\n...",
    "scenario_name": "通用模板"
}
```

**使用示例**：
```python
result = get_prompt_template()
prompt = result["template"]
# 替换模板中的图片路径后使用
```

---

#### 6. `get_usage_guide`

**功能**：获取完整的使用指南、技巧和示例

**参数**：无

**返回**：
```python
{
    "guide": "使用指南内容...",
    "tips": "使用技巧...",
    "examples": "实用示例..."
}
```

**使用示例**：
```python
guide = get_usage_guide()
print(guide["guide"])  # 查看使用指南
print(guide["tips"])   # 查看使用技巧
print(guide["examples"])  # 查看示例
```

---

## 🎯 工具选择建议

### OCR引擎选择

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 中文文档 | `recognize_image_paddleocr` | 中文识别准确率高，速度快 |
| 多语言文档 | `recognize_image_easyocr` | 支持80+语言 |
| 官方MCP实现 | `recognize_image_paddleocr_mcp` | 标准化接口 |
| 高准确率需求 | `recognize_image_paddleocr` | DeepSeek不推荐，资源消耗大 |

### 工作流程

1. **OCR识别** → 使用 `recognize_image_*` 工具
2. **获取模板** → 使用 `get_prompt_template` 获取示例模板
3. **参考指南** → 使用 `get_usage_guide` 查看使用技巧

---

## 📝 注意事项

1. **图片路径**：支持绝对路径和相对路径
2. **错误处理**：所有工具在出错时返回包含 `error` 字段的字典
3. **日志记录**：所有工具调用都会记录日志，可通过 Cursor 输出面板查看
4. **性能**：PaddleOCR 和 EasyOCR 性能较好，DeepSeek 较慢

---

## 🔗 相关文档

- [README.md](../README.md) - 项目主文档
- [prompt_template.md](../prompt_template.md) - Prompt模板详细说明
- [Prompt使用方式变更说明.md](Prompt使用方式变更说明.md) - 使用方式变更历史

