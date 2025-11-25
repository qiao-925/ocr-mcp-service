"""
OCR MCP服务器 - 基于PaddleOCR的图片文字识别服务

使用FastMCP框架实现，支持通过MCP协议为AI Agent提供OCR能力。
"""

import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from paddleocr import PaddleOCR

# 配置日志
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "mcp_ocr_server.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"日志文件位置: {log_file}")

# 创建FastMCP服务器实例
mcp = FastMCP("OCR Service")

# 全局OCR实例（延迟初始化）
_ocr_instance: PaddleOCR | None = None


def get_ocr_instance() -> PaddleOCR:
    """获取OCR实例（单例模式，延迟初始化）"""
    global _ocr_instance
    if _ocr_instance is None:
        logger.info("初始化PaddleOCR...")
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang='ch')
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
            error_msg = f"文件不存在: {image_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "text": "",
                "lines": []
            }
        
        if not path.is_file():
            error_msg = f"路径不是文件: {image_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "text": "",
                "lines": []
            }
        
        logger.info(f"开始OCR识别: {image_path}")
        
        # 获取OCR实例并执行识别
        ocr = get_ocr_instance()
        result = ocr.ocr(str(path))
        
        # 调试：记录返回结果的结构
        logger.info(f"OCR返回结果类型: {type(result)}")
        if result is not None:
            logger.info(f"result是否为None: False")
            if isinstance(result, (list, tuple)):
                logger.info(f"result是列表/元组，长度: {len(result)}")
                if len(result) > 0:
                    logger.info(f"result[0]类型: {type(result[0])}")
                    if isinstance(result[0], (list, tuple)):
                        logger.info(f"result[0]是列表/元组，长度: {len(result[0])}")
                        if len(result[0]) > 0:
                            logger.info(f"result[0][0]类型: {type(result[0][0])}, 内容: {str(result[0][0])[:200]}")
                    elif isinstance(result[0], str):
                        logger.warning(f"result[0]是字符串，内容: {result[0][:200]}")
            elif isinstance(result, str):
                logger.warning(f"result是字符串，内容: {result[:200]}")
        else:
            logger.warning("OCR返回结果为None")
        
        # 处理识别结果
        texts = []
        lines = []
        
        # 检查result格式
        if result is None:
            logger.warning("OCR返回结果为None")
        elif isinstance(result, str):
            logger.warning(f"OCR返回结果是字符串而不是列表: {result[:200]}")
        elif not isinstance(result, (list, tuple)) or len(result) == 0:
            logger.warning(f"OCR返回结果格式异常: {type(result)}, 长度: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        elif isinstance(result[0], str):
            logger.warning(f"result[0]是字符串: {result[0][:200]}")
        elif result and result[0]:
            for line in result[0]:
                if line:
                    # 如果line是字符串，说明数据格式不对
                    if isinstance(line, str):
                        logger.warning(f"line是字符串而不是列表: {line[:100]}")
                        continue
                    for word_info in line:
                        try:
                            # PaddleOCR返回格式: [[坐标], (文本, 置信度)]
                            if (len(word_info) >= 2 and 
                                isinstance(word_info[1], (list, tuple)) and 
                                len(word_info[1]) >= 2):
                                
                                text = word_info[1][0]  # 识别的文本
                                confidence = word_info[1][1]  # 置信度
                                bbox = word_info[0]  # 边界框坐标
                                
                                texts.append(text)
                                lines.append({
                                    "text": text,
                                    "confidence": round(confidence, 4),
                                    "bbox": [[round(p[0]), round(p[1])] for p in bbox] if bbox else []
                                })
                            else:
                                logger.warning(f"意外的word_info格式: {word_info}")
                        except (IndexError, TypeError) as e:
                            logger.warning(f"解析word_info时出错: {word_info}, 错误: {e}")
                            continue
        
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
