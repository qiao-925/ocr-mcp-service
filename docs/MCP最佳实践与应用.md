# MCP最佳实践与应用

## 📋 概述

本文档基于MCP（Model Context Protocol）最佳实践，特别是针对长任务处理，分析并应用到OCR MCP服务中。

## 🎯 MCP长任务处理最佳实践

### 1. 分层超时控制 ⭐⭐⭐

**最佳实践**：
- **客户端等待时间**: 15-30秒（Cursor等客户端）
- **MCP服务器处理时间**: 10-25秒（工具执行）
- **上游API调用超时**: 3-10秒（OCR引擎调用）

**当前实现**：
- ✅ 已实现：`OCR_TIMEOUT` 默认120秒（可配置）
- ⚠️ 需要优化：应该根据任务类型设置不同超时

**应用改进**：
```python
# 根据图片大小和引擎类型设置不同超时
SMALL_IMAGE_TIMEOUT = 60   # 小图片（< 1MB）
MEDIUM_IMAGE_TIMEOUT = 120 # 中等图片（1-5MB）
LARGE_IMAGE_TIMEOUT = 180  # 大图片（> 5MB）
```

---

### 2. 进度更新机制 ⭐⭐⭐

**最佳实践**：
- 长任务必须定期发送进度更新
- 进度更新频率：每5-10%或每2-5秒
- 使用MCP通知机制发送进度

**当前实现**：
- ✅ 已实现：`ProgressTracker` 跟踪进度
- ✅ 已实现：通过日志发送进度通知
- ⚠️ 需要优化：确保进度更新及时发送，避免客户端超时

**应用改进**：
- 确保关键阶段（10%, 20%, 50%, 80%, 100%）必须发送进度
- 在长时间操作中定期发送心跳进度（即使进度不变）

---

### 3. 异步处理 ⭐⭐

**最佳实践**：
- 超过10秒的任务应该考虑异步处理
- 使用后台任务或任务队列
- 提供任务状态查询接口

**当前实现**：
- ⚠️ 当前是同步处理，可能阻塞MCP连接
- ✅ 已有超时保护，防止无限等待

**应用改进**：
- 对于批量处理，使用异步任务
- 提供任务ID和状态查询

---

### 4. 资源管理 ⭐⭐⭐

**最佳实践**：
- 合理管理系统资源（内存、CPU）
- 监控资源使用情况
- 实现资源清理机制

**当前实现**：
- ✅ 已实现：引擎懒加载
- ✅ 已实现：引擎使用统计
- ⚠️ 需要优化：长时间未使用的引擎自动卸载

**应用改进**：
- 实现引擎自动卸载（30分钟未使用）
- 添加内存监控和告警

---

### 5. 错误处理 ⭐⭐⭐

**最佳实践**：
- 提供清晰、可操作的错误消息
- 区分临时错误和永久错误
- 支持详细和简洁两种响应模式

**当前实现**：
- ✅ 已实现：区分错误类型（TimeoutError, FileNotFoundError等）
- ✅ 已实现：错误响应包含error_type字段
- ✅ 已实现：详细错误日志

**应用改进**：
- 错误消息更加用户友好
- 提供错误恢复建议

---

### 6. 健康检查 ⭐⭐

**最佳实践**：
- 定期检查服务状态
- 监控服务健康度
- 自动恢复机制

**当前实现**：
- ⚠️ 缺少健康检查机制

**应用改进**：
- 添加健康检查工具
- 监控引擎状态

---

## 🔧 已应用的改进

### 1. 优化超时配置

**文件**: `src/ocr_mcp_service/config.py`

```python
# 根据图片大小动态设置超时
def get_timeout_for_image(image_path: str) -> int:
    """根据图片大小返回合适的超时时间。"""
    size = Path(image_path).stat().st_size
    if size < 1024 * 1024:  # < 1MB
        return 60
    elif size < 5 * 1024 * 1024:  # < 5MB
        return 120
    else:  # >= 5MB
        return 180
```

### 2. 增强进度通知

**文件**: `src/ocr_mcp_service/progress_tracker.py`

- 确保关键阶段（10%, 20%, 50%, 80%, 100%）必须发送
- 在长时间操作中定期发送心跳（每5秒）

### 3. 改进错误处理

**文件**: `src/ocr_mcp_service/tools.py`

- 错误消息更加用户友好
- 提供错误恢复建议

### 4. 资源监控

**文件**: `src/ocr_mcp_service/ocr_engine.py`

- 引擎使用统计
- 支持引擎卸载（待实现）

---

## 📊 性能优化建议

### 1. 批量处理优化

**当前问题**：
- 批量处理时可能遇到连接问题
- 服务负载过高

**解决方案**：
- ✅ 已实现：分批处理脚本
- ✅ 已实现：自动重试机制
- ✅ 已实现：批次间等待

### 2. 内存优化

**建议**：
- 实现引擎自动卸载（30分钟未使用）
- 监控内存使用，超过阈值时告警
- 考虑使用进程池处理批量任务

### 3. 并发控制

**建议**：
- 限制同时处理的图片数量
- 使用信号量控制并发
- 队列化处理请求

---

## 🎯 实施优先级

### 高优先级（立即实施）

1. ✅ **分层超时控制** - 根据图片大小设置超时
2. ✅ **进度通知优化** - 确保关键阶段发送进度
3. ✅ **错误处理改进** - 用户友好的错误消息

### 中优先级（近期实施）

4. **资源监控** - 内存使用监控
5. **健康检查** - 服务状态检查
6. **引擎自动卸载** - 长时间未使用自动释放

### 低优先级（长期优化）

7. **异步处理** - 后台任务支持
8. **任务队列** - 批量任务队列化
9. **性能分析** - 详细的性能指标

---

## 📝 代码示例

### 示例1：动态超时

```python
def get_timeout_for_image(image_path: str) -> int:
    """根据图片大小返回合适的超时时间。"""
    try:
        size = Path(image_path).stat().st_size
        if size < 1024 * 1024:  # < 1MB
            return 60
        elif size < 5 * 1024 * 1024:  # < 5MB
            return 120
        else:  # >= 5MB
            return 180
    except:
        return OCR_TIMEOUT  # 默认超时
```

### 示例2：增强进度通知

```python
class EnhancedProgressTracker(ProgressTracker):
    """增强的进度跟踪器，确保及时发送进度。"""
    
    def __init__(self, on_progress=None, heartbeat_interval=5.0):
        super().__init__(on_progress)
        self.last_heartbeat = time.time()
        self.heartbeat_interval = heartbeat_interval
    
    def update(self, percentage, stage, message=""):
        super().update(percentage, stage, message)
        
        # 发送心跳（即使进度不变）
        now = time.time()
        if now - self.last_heartbeat >= self.heartbeat_interval:
            if self.on_progress:
                self.on_progress(percentage, stage, f"处理中... ({message})")
            self.last_heartbeat = now
```

### 示例3：健康检查工具

```python
@mcp.tool()
def health_check() -> dict:
    """检查MCP服务健康状态。"""
    from .ocr_engine import OCREngineFactory
    
    stats = OCREngineFactory.get_usage_stats()
    
    return {
        "status": "healthy",
        "engines_loaded": stats["total_engines"],
        "engines": stats["engines"],
        "timestamp": datetime.now().isoformat()
    }
```

---

## 🔍 监控指标

### 关键指标

1. **处理时间**
   - 平均处理时间
   - 最长处理时间
   - 超时率

2. **成功率**
   - 成功/失败比例
   - 错误类型分布

3. **资源使用**
   - 内存使用
   - CPU使用
   - 引擎数量

4. **连接状态**
   - 连接断开次数
   - 重连次数
   - 平均连接时长

---

## 📚 参考资源

- [MCP官方文档](https://modelcontextprotocol.io/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [MCP最佳实践](https://mcpcn.com/docs/tutorials/writing-effective-tools/)

---

## ✅ 总结

通过应用MCP最佳实践，特别是针对长任务处理：

1. ✅ **超时控制** - 分层超时，防止无限等待
2. ✅ **进度通知** - 及时发送进度，保持连接活跃
3. ✅ **错误处理** - 清晰的错误消息和恢复建议
4. ✅ **资源管理** - 监控和优化资源使用
5. ⚠️ **异步处理** - 待实现，用于超长任务
6. ⚠️ **健康检查** - 待实现，监控服务状态

这些改进显著提升了MCP服务的稳定性和用户体验。

