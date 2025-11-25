# Python项目运行方式指南

本文档介绍Python生态中常见的项目运行方式及其适用场景。

## 📚 Python项目运行方式概览

### 1. Entry Points (console_scripts) - ⭐ 推荐

**定义**：在`pyproject.toml`中定义可执行命令，安装后可直接运行。

**优点**：
- ✅ Python标准实践（PEP 517/518）
- ✅ 安装后可直接使用命令名运行
- ✅ 自动处理虚拟环境
- ✅ 跨平台兼容

**实现方式**：

```toml
[project.scripts]
ocr-mcp-server = "ocr_mcp_service.__main__:main"
```

**使用方式**：
```bash
# 安装项目（开发模式）
pip install -e .

# 或使用uv
uv pip install -e .

# 然后直接运行
ocr-mcp-server
```

**适用场景**：
- 可安装的Python包
- 需要作为命令行工具使用
- 希望用户通过命令名直接运行

---

### 2. Python模块方式 (`python -m`) - ⭐ 推荐

**定义**：将项目作为Python模块运行。

**优点**：
- ✅ Python标准实践
- ✅ 不需要安装项目
- ✅ 自动处理模块路径
- ✅ 适合开发和测试

**实现方式**：

创建`src/ocr_mcp_service/__main__.py`：
```python
"""模块入口点。"""
from ocr_mcp_service.mcp_server import mcp

if __name__ == "__main__":
    mcp.run()
```

**使用方式**：
```bash
# 在项目根目录
python -m ocr_mcp_service

# 或使用uv（自动在虚拟环境中运行）
uv run python -m ocr_mcp_service
```

**适用场景**：
- 开发阶段
- 测试和调试
- 不需要安装的项目

---

### 3. 直接运行脚本 (`python script.py`)

**定义**：直接运行Python脚本文件。

**优点**：
- ✅ 最简单直接
- ✅ 不需要配置

**缺点**：
- ❌ 需要手动激活虚拟环境
- ❌ 路径处理可能有问题
- ❌ 不适合作为可安装包

**使用方式**：
```bash
# 需要先激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 然后运行
python mcp_ocr_server.py
```

**适用场景**：
- 简单脚本
- 一次性任务
- 不需要分发的项目

---

### 4. uv run - 便利工具

**定义**：uv提供的便利命令，自动在虚拟环境中运行。

**优点**：
- ✅ 自动管理虚拟环境
- ✅ 不需要手动激活
- ✅ 适合开发阶段

**缺点**：
- ❌ 依赖uv工具
- ❌ 不是Python标准实践
- ❌ 不适合生产环境配置

**使用方式**：
```bash
uv run python mcp_ocr_server.py
uv run python -m ocr_mcp_service
```

**适用场景**：
- 开发阶段
- 快速测试
- 使用uv管理的项目

---

### 5. Makefile - 传统但有效

**定义**：使用Makefile封装常用命令。

**优点**：
- ✅ 跨语言通用
- ✅ 命令简洁
- ✅ 适合复杂工作流

**缺点**：
- ❌ Windows需要额外工具
- ❌ 需要学习Make语法

**实现方式**：

```makefile
.PHONY: install run test clean

install:
	uv sync

run:
	uv run python -m ocr_mcp_service

test:
	uv run pytest

clean:
	rm -rf __pycache__ .pytest_cache
```

**使用方式**：
```bash
make install
make run
make test
```

**适用场景**：
- 需要复杂工作流的项目
- 团队协作
- CI/CD集成

---

### 6. 任务运行器（Task Runners）

#### 6.1 Poetry + Scripts

```toml
[tool.poetry.scripts]
ocr-server = "ocr_mcp_service.__main__:main"
```

#### 6.2 poethepoet

```toml
[tool.poe.tasks]
run = "python -m ocr_mcp_service"
test = "pytest"
```

#### 6.3 taskipy

```toml
[tool.taskipy.tasks]
run = "python -m ocr_mcp_service"
test = "pytest"
```

---

## 🎯 针对MCP服务器的推荐方案

### 方案A：Entry Points（⭐ 最推荐）

**配置**：
1. 在`pyproject.toml`中定义entry point
2. 添加`__main__.py`支持`python -m`方式（作为备选）

**优点**：
- ✅ 最符合Python生产实践
- ✅ 命令简洁：`ocr-mcp-server`
- ✅ Cursor配置最简单：直接调用命令
- ✅ 跨平台兼容
- ✅ 自动处理虚拟环境

**使用**：
```bash
# 安装项目
pip install -e .  # 或 uv pip install -e .

# 运行
ocr-mcp-server
```

**Cursor配置**：
```json
{
  "command": "/path/to/.venv/bin/ocr-mcp-server",
  "args": []
}
```

### 方案B：Python模块方式（备选）

**配置**：
1. 添加`__main__.py`
2. 不定义entry point（或作为备选）

**优点**：
- 简单直接
- 不需要安装项目
- 适合开发阶段

**使用**：
```bash
python -m ocr_mcp_service
```

**Cursor配置**：
```json
{
  "command": "/path/to/.venv/bin/python",
  "args": ["-m", "ocr_mcp_service"]
}
```

---

## 📊 对比总结

| 方式 | 标准性 | 便利性 | 适用场景 | 推荐度 |
|------|--------|--------|----------|--------|
| Entry Points | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 可安装包 | ⭐⭐⭐⭐⭐ |
| `python -m` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 开发/测试 | ⭐⭐⭐⭐⭐ |
| 直接运行 | ⭐⭐⭐ | ⭐⭐⭐ | 简单脚本 | ⭐⭐⭐ |
| `uv run` | ⭐⭐ | ⭐⭐⭐⭐⭐ | 开发阶段 | ⭐⭐⭐⭐ |
| Makefile | ⭐⭐⭐ | ⭐⭐⭐⭐ | 复杂工作流 | ⭐⭐⭐⭐ |

---

## 🔧 实际应用建议

### 对于MCP服务器项目：

1. **开发阶段**：
   - 使用 `python -m ocr_mcp_service` 或 `uv run python -m ocr_mcp_service`
   - 添加Makefile方便常用操作

2. **Cursor配置**：
   ```json
   {
     "command": "python",
     "args": ["-m", "ocr_mcp_service"],
     "env": {
       "PYTHONPATH": "/path/to/ocr-mcp-service/src"
     }
   }
   ```
   或使用虚拟环境中的Python：
   ```json
   {
     "command": "/path/to/ocr-mcp-service/.venv/bin/python",
     "args": ["-m", "ocr_mcp_service"]
   }
   ```

3. **生产部署**：
   - 安装项目：`pip install -e .` 或 `uv pip install -e .`
   - 使用entry point：`ocr-mcp-server`

---

## 📚 参考资源

- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - Specifying Build System Dependencies](https://peps.python.org/pep-0518/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [uv Documentation](https://github.com/astral-sh/uv)

