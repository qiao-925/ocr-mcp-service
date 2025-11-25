"""
OCR MCP服务器 - 基于PaddleOCR的图片文字识别服务

使用FastMCP框架实现，支持通过MCP协议为AI Agent提供OCR能力。
"""

import base64
import logging
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from paddleocr import PaddleOCR

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastMCP服务器实例
mcp = FastMCP("OCR Service")

# 全局OCR实例（延迟初始化）
_ocr_instance: PaddleOCR | None = None


def get_ocr_instance() -> PaddleOCR:
    """获取OCR实例（单例模式，延迟初始化）"""
    global _ocr_instance
    if _ocr_instance is None:
        logger.info("初始化PaddleOCR...")
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
        logger.info("PaddleOCR初始化完成")
    return _ocr_instance


@mcp.tool()
def recognize_text_from_path(image_path: str) -> dict[str, Any]:
    """
    从图片文件路径识别文字
    
    Args:
        image_path: 图片文件的路径（绝对路径或相对路径）
    
    Returns:
        包含识别结果的字典：
        - text: 识别出的完整文本
        - lines: 按行组织的识别结果列表，每行包含文本、置信度和位置信息
        - success: 是否成功
        - error: 错误信息（如果有）
    """
    try:
        # 验证文件路径
        path = Path(image_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"文件不存在: {image_path}",
                "text": "",
                "lines": []
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"路径不是文件: {image_path}",
                "text": "",
                "lines": []
            }
        
        logger.info(f"开始OCR识别: {image_path}")
        
        # 获取OCR实例并执行识别
        ocr = get_ocr_instance()
        result = ocr.ocr(str(path))
        
        # 处理识别结果
        texts = []
        lines = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    for word_info in line:
                        text = word_info[1][0]  # 识别的文本
                        confidence = word_info[1][1]  # 置信度
                        bbox = word_info[0]  # 边界框坐标
                        
                        texts.append(text)
                        lines.append({
                            "text": text,
                            "confidence": round(confidence, 4),
                            "bbox": [[round(p[0]), round(p[1])] for p in bbox]
                        })
        
        full_text = "\n".join(texts)
        
        logger.info(f"OCR识别完成，共识别 {len(lines)} 个文本块")
        
        return {
            "success": True,
            "text": full_text,
            "lines": lines,
            "line_count": len(lines)
        }
        
    except Exception as e:
        logger.error(f"OCR识别失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "text": "",
            "lines": []
        }


@mcp.tool()
def recognize_text_from_base64(image_base64: str) -> dict[str, Any]:
    """
    从base64编码的图片数据识别文字
    
    Args:
        image_base64: base64编码的图片数据（可包含data:image/xxx;base64,前缀）
    
    Returns:
        包含识别结果的字典：
        - text: 识别出的完整文本
        - lines: 按行组织的识别结果列表，每行包含文本、置信度和位置信息
        - success: 是否成功
        - error: 错误信息（如果有）
    """
    try:
        import io
        from PIL import Image
        
        # 处理base64数据（移除可能的前缀）
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # 解码base64
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        logger.info(f"开始OCR识别base64图片，尺寸: {image.size}")
        
        # 获取OCR实例并执行识别
        ocr = get_ocr_instance()
        result = ocr.ocr(image)
        
        # 处理识别结果
        texts = []
        lines = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    for word_info in line:
                        text = word_info[1][0]  # 识别的文本
                        confidence = word_info[1][1]  # 置信度
                        bbox = word_info[0]  # 边界框坐标
                        
                        texts.append(text)
                        lines.append({
                            "text": text,
                            "confidence": round(confidence, 4),
                            "bbox": [[round(p[0]), round(p[1])] for p in bbox]
                        })
        
        full_text = "\n".join(texts)
        
        logger.info(f"OCR识别完成，共识别 {len(lines)} 个文本块")
        
        return {
            "success": True,
            "text": full_text,
            "lines": lines,
            "line_count": len(lines)
        }
        
    except Exception as e:
        logger.error(f"OCR识别失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "text": "",
            "lines": []
        }


if __name__ == "__main__":
    # 运行MCP服务器（使用stdio传输）
    mcp.run()

