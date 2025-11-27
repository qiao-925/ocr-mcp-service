"""Technical analysis generator for OCR results."""

from typing import Optional, Dict, Any, List
from .models import OCRResult


class AnalysisGenerator:
    """Generate technical analysis description for OCR results."""

    def __init__(self):
        """Initialize the analysis generator."""
        pass

    def generate_analysis(
        self, ocr_result: OCRResult, layout_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate technical analysis description.

        Args:
            ocr_result: OCR recognition result
            layout_info: Optional layout analysis information

        Returns:
            Technical analysis description in Chinese
        """
        lines = []

        # Basic metrics
        basic_info = self._analyze_basic_metrics(ocr_result)
        lines.extend(basic_info)

        # Text statistics
        text_stats = self._analyze_text_statistics(ocr_result)
        if text_stats:
            lines.append("")
            lines.extend(text_stats)

        # Layout information (if available)
        if layout_info:
            layout_info_lines = self._analyze_layout_info(layout_info)
            if layout_info_lines:
                lines.append("")
                lines.extend(layout_info_lines)

        # Quality assessment
        quality_info = self._generate_quality_assessment(ocr_result)
        if quality_info:
            lines.append("")
            lines.extend(quality_info)

        return "\n".join(lines)

    def _analyze_basic_metrics(self, ocr_result: OCRResult) -> List[str]:
        """Analyze basic metrics."""
        lines = []
        lines.append("【技术解析】")
        lines.append(f"识别引擎: {ocr_result.engine}")
        lines.append(f"处理时间: {ocr_result.processing_time:.2f}秒")

        # Confidence rating
        confidence_rating = self._get_confidence_rating(ocr_result.confidence)
        lines.append(
            f"识别置信度: {ocr_result.confidence:.2f} ({confidence_rating['level']})"
        )
        lines.append(f"文本框数量: {len(ocr_result.boxes)}个")

        return lines

    def _analyze_text_statistics(self, ocr_result: OCRResult) -> List[str]:
        """Analyze text statistics."""
        lines = []
        lines.append("文本统计:")

        # Character count (excluding whitespace)
        char_count = len(ocr_result.text.replace(" ", "").replace("\n", ""))
        lines.append(f"- 总字符数: {char_count}")

        # Line count
        line_count = len([line for line in ocr_result.text.split("\n") if line.strip()])
        if line_count > 0:
            lines.append(f"- 文本行数: {line_count}行")

        # Simple paragraph detection based on empty lines
        paragraphs_text = [
            p.strip() for p in ocr_result.text.split("\n\n") if p.strip()
        ]
        if len(paragraphs_text) > 1:
            lines.append(f"- 段落数量: {len(paragraphs_text)}段（基于空行分析）")
        elif len(paragraphs_text) == 1 and line_count > 1:
            lines.append("- 段落数量: 1段")

        return lines

    def _analyze_layout_info(self, layout_info: Dict[str, Any]) -> List[str]:
        """Analyze layout information."""
        lines = []
        lines.append("版式特征:")

        # Paragraph count from layout analysis
        if "paragraph_count" in layout_info:
            lines.append(f"- 段落数量: {layout_info['paragraph_count']}段（基于位置分析）")

        # Underline count
        if "underline_count" in layout_info:
            underline_count = layout_info["underline_count"]
            if underline_count > 0:
                lines.append(f"- 下划线: {underline_count}处")
            else:
                lines.append("- 下划线: 无")

        # Alignment
        if "alignment" in layout_info:
            alignment = layout_info["alignment"]
            alignment_map = {
                "left": "左对齐",
                "right": "右对齐",
                "center": "居中对齐",
                "justify": "两端对齐",
            }
            alignment_text = alignment_map.get(alignment, alignment)
            lines.append(f"- 主要对齐方式: {alignment_text}")

        return lines

    def _generate_quality_assessment(self, ocr_result: OCRResult) -> List[str]:
        """Generate quality assessment."""
        lines = []
        lines.append("质量评估:")

        # Confidence rating
        rating = self._get_confidence_rating(ocr_result.confidence)
        lines.append(
            f"- 置信度评级: {rating['level']} ({rating['threshold']})"
        )

        # Quality description
        quality_desc = self._get_quality_description(ocr_result)
        lines.append(f"- 识别质量: {quality_desc}")

        # Suggestions
        suggestion = self._get_suggestion(ocr_result)
        if suggestion:
            lines.append(f"- 建议: {suggestion}")

        return lines

    def _get_confidence_rating(self, confidence: float) -> Dict[str, str]:
        """Get confidence rating."""
        if confidence >= 0.9:
            return {"level": "优秀", "threshold": "≥0.9"}
        elif confidence >= 0.7:
            return {"level": "良好", "threshold": "0.7-0.9"}
        else:
            return {"level": "一般", "threshold": "<0.7"}

    def _get_quality_description(self, ocr_result: OCRResult) -> str:
        """Get quality description."""
        if ocr_result.confidence >= 0.9:
            return "高，文本清晰可读"
        elif ocr_result.confidence >= 0.7:
            return "中等，建议检查关键内容"
        else:
            return "较低，建议人工校对"

    def _get_suggestion(self, ocr_result: OCRResult) -> str:
        """Get suggestion based on OCR result."""
        if ocr_result.confidence >= 0.9:
            return "识别结果可靠，可直接使用"
        elif ocr_result.confidence >= 0.7:
            return "识别结果基本可靠，建议检查重要内容"
        else:
            return "识别质量较低，建议人工校对或重新识别"

