"""OCR引擎封装模块。

统一PaddleOCR初始化和结果处理。
"""

import logging
from typing import Any

from paddleocr import PaddleOCR

from ocr_mcp_service.config import OCRConfig, default_config

logger = logging.getLogger(__name__)


class OCREngine:
    """OCR引擎封装类。

    使用单例模式管理PaddleOCR实例，提供统一的OCR识别接口。
    """

    _instance: PaddleOCR | None = None
    _config: OCRConfig | None = None

    def __init__(self, config: OCRConfig | None = None) -> None:
        """初始化OCR引擎。

        Args:
            config: OCR配置，默认使用default_config
        """
        self._config = config or default_config

    @classmethod
    def get_instance(cls, config: OCRConfig | None = None) -> PaddleOCR:
        """获取OCR实例（单例模式，延迟初始化）。

        使用PaddleOCR 3.x，默认PP-OCRv5_server模型，支持中文识别和角度分类。

        Args:
            config: OCR配置，默认使用default_config

        Returns:
            PaddleOCR: OCR实例

        Raises:
            RuntimeError: 当OCR初始化失败时抛出
        """
        if cls._instance is None:
            cfg = config or default_config
            try:
                logger.info(
                    f"初始化PaddleOCR（PP-OCRv5_server模型，语言={cfg.lang}，角度分类={cfg.use_angle_cls}）..."
                )
                cls._instance = PaddleOCR(use_angle_cls=cfg.use_angle_cls, lang=cfg.lang)
                cls._config = cfg
                logger.info("PaddleOCR初始化完成")
            except Exception as e:
                logger.error(f"PaddleOCR初始化失败: {e}", exc_info=True)
                raise RuntimeError(f"OCR引擎初始化失败: {e}") from e
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置OCR实例（用于测试或重新配置）。"""
        cls._instance = None
        cls._config = None
        logger.info("OCR实例已重置")

    @staticmethod
    def parse_result(result: list[Any] | None) -> tuple[str, list[dict[str, Any]]]:
        """解析PaddleOCR识别结果。

        PaddleOCR 3.x返回格式：
        result = [
            {
                'rec_texts': ['文本1', '文本2', ...],
                'rec_scores': [0.99, 0.98, ...],
                'rec_polys': array([[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], ...])
            }
        ]

        Args:
            result: PaddleOCR返回的识别结果

        Returns:
            tuple[str, list[dict]]: (完整文本, 行信息列表)
        """
        if not result or not isinstance(result, list) or len(result) == 0:
            return "", []

        texts: list[str] = []
        lines: list[dict[str, Any]] = []

        # 处理第一页结果（通常只有一页）
        page_result = result[0] if result else None
        
        # 检查是否是OCRResult对象（PaddleOCR 3.x）
        try:
            if hasattr(page_result, 'rec_texts'):
                # OCRResult对象，直接访问属性
                rec_texts = page_result.rec_texts if hasattr(page_result, 'rec_texts') else []
                rec_scores = page_result.rec_scores if hasattr(page_result, 'rec_scores') else []
                rec_polys = page_result.rec_polys if hasattr(page_result, 'rec_polys') else []
            elif isinstance(page_result, dict):
                # 字典格式（兼容处理）
                rec_texts = page_result.get('rec_texts', [])
                rec_scores = page_result.get('rec_scores', [])
                rec_polys = page_result.get('rec_polys', [])
            else:
                # 旧格式或其他格式
                rec_texts = []
                rec_scores = []
                rec_polys = []
                
                # 确保列表长度一致
                min_len = min(len(rec_texts), len(rec_scores), len(rec_polys))
                
                for i in range(min_len):
                    text = str(rec_texts[i]).strip()
                    # 跳过空文本
                    if not text:
                        continue
                    
                    confidence = float(rec_scores[i]) if i < len(rec_scores) else 0.0
                    bbox_array = rec_polys[i] if i < len(rec_polys) else None
                    
                    # 格式化边界框坐标
                    from ocr_mcp_service.utils import format_bbox
                    
                    if bbox_array is not None:
                        # 将numpy数组转换为列表格式
                        if hasattr(bbox_array, 'tolist'):
                            bbox = bbox_array.tolist()
                        else:
                            bbox = list(bbox_array)
                        formatted_bbox = format_bbox(bbox)
                    else:
                        formatted_bbox = []
                    
                    texts.append(text)
                    lines.append(
                        {
                            "text": text,
                            "confidence": round(confidence, 4),
                            "bbox": formatted_bbox,
                        }
                    )
            except (KeyError, TypeError, ValueError, IndexError) as e:
                logger.warning(f"解析新格式结果时出错: {e}", exc_info=True)
                return "", []
        # 兼容旧格式（列表格式）
        elif isinstance(page_result, list):
            for line_data in page_result:
                if not line_data or len(line_data) < 2:
                    continue

                try:
                    # 提取边界框坐标
                    bbox = line_data[0]
                    # 提取文本和置信度
                    text_info = line_data[1]

                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        text = str(text_info[0])
                        confidence = float(text_info[1])
                    else:
                        logger.warning(f"意外的文本信息格式: {text_info}")
                        continue

                    # 格式化边界框坐标
                    from ocr_mcp_service.utils import format_bbox

                    formatted_bbox = format_bbox(bbox)

                    texts.append(text)
                    lines.append(
                        {
                            "text": text,
                            "confidence": round(confidence, 4),
                            "bbox": formatted_bbox,
                        }
                    )
                except (IndexError, TypeError, ValueError) as e:
                    logger.warning(f"解析行数据时出错: {line_data}, 错误: {e}")
                    continue
        else:
            logger.warning(f"意外的结果格式: {type(page_result)}")
            return "", []

        full_text = "\n".join(texts)
        return full_text, lines

