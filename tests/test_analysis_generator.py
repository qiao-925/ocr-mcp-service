"""分析生成器测试"""

import pytest
from ocr_mcp_service.analysis_generator import AnalysisGenerator
from ocr_mcp_service.models import OCRResult, BoundingBox


def test_analysis_generator_init():
    """测试AnalysisGenerator初始化"""
    generator = AnalysisGenerator()
    assert generator is not None


def test_generate_analysis_basic():
    """测试生成基本分析"""
    generator = AnalysisGenerator()
    
    result = OCRResult(
        text="测试文本",
        boxes=[BoundingBox(x1=0, y1=0, x2=100, y2=20)],
        confidence=0.95,
        engine="paddleocr",
        processing_time=1.5
    )
    
    analysis = generator.generate_analysis(result)
    
    assert isinstance(analysis, str)
    assert "技术解析" in analysis
    assert "paddleocr" in analysis
    assert "1.5" in analysis
    assert "0.95" in analysis


def test_generate_analysis_empty_text():
    """测试空文本分析"""
    generator = AnalysisGenerator()
    
    result = OCRResult(
        text="",
        boxes=[],
        confidence=0.0,
        engine="test",
        processing_time=0.0
    )
    
    analysis = generator.generate_analysis(result)
    
    assert isinstance(analysis, str)
    assert "技术解析" in analysis
    assert "0个" in analysis  # 文本框数量


def test_generate_analysis_with_layout_info():
    """测试带版式信息的分析"""
    generator = AnalysisGenerator()
    
    result = OCRResult(
        text="测试文本\n第二行",
        boxes=[BoundingBox(x1=0, y1=0, x2=100, y2=20)],
        confidence=0.85,
        engine="test",
        processing_time=1.0
    )
    
    layout_info = {
        "paragraph_count": 2,
        "underline_count": 1,
        "alignment": "left"
    }
    
    analysis = generator.generate_analysis(result, layout_info)
    
    assert "版式特征" in analysis
    assert "2段" in analysis
    assert "1处" in analysis  # 下划线
    assert "左对齐" in analysis


def test_analyze_basic_metrics():
    """测试基本指标分析"""
    generator = AnalysisGenerator()
    
    result = OCRResult(
        text="测试",
        boxes=[BoundingBox(x1=0, y1=0, x2=50, y2=20)],
        confidence=0.9,
        engine="test",
        processing_time=0.5
    )
    
    metrics = generator._analyze_basic_metrics(result)
    
    assert isinstance(metrics, list)
    assert len(metrics) > 0
    assert "技术解析" in metrics[0]
    assert any("test" in m for m in metrics)
    assert any("0.5" in m for m in metrics)
    assert any("0.9" in m for m in metrics)
    assert any("1个" in m for m in metrics)


def test_analyze_text_statistics():
    """测试文本统计"""
    generator = AnalysisGenerator()
    
    # 测试多行文本
    result = OCRResult(
        text="第一行\n第二行\n第三行",
        boxes=[],
        confidence=0.8,
        engine="test",
        processing_time=1.0
    )
    
    stats = generator._analyze_text_statistics(result)
    
    assert isinstance(stats, list)
    assert "文本统计" in stats[0]
    assert any("3行" in s for s in stats)
    
    # 测试空文本
    result_empty = OCRResult(
        text="",
        boxes=[],
        confidence=0.0,
        engine="test",
        processing_time=0.0
    )
    
    stats_empty = generator._analyze_text_statistics(result_empty)
    assert isinstance(stats_empty, list)


def test_analyze_text_statistics_paragraphs():
    """测试段落检测"""
    generator = AnalysisGenerator()
    
    # 测试多段落文本
    result = OCRResult(
        text="第一段\n\n第二段\n\n第三段",
        boxes=[],
        confidence=0.8,
        engine="test",
        processing_time=1.0
    )
    
    stats = generator._analyze_text_statistics(result)
    
    assert any("3段" in s for s in stats)


def test_analyze_layout_info():
    """测试版式信息分析"""
    generator = AnalysisGenerator()
    
    layout_info = {
        "paragraph_count": 3,
        "underline_count": 2,
        "alignment": "center"
    }
    
    info = generator._analyze_layout_info(layout_info)
    
    assert isinstance(info, list)
    assert "版式特征" in info[0]
    assert any("3段" in i for i in info)
    assert any("2处" in i for i in info)
    assert any("居中" in i for i in info)


def test_analyze_layout_info_no_underline():
    """测试无下划线的版式信息"""
    generator = AnalysisGenerator()
    
    layout_info = {
        "paragraph_count": 1,
        "underline_count": 0,
        "alignment": "right"
    }
    
    info = generator._analyze_layout_info(layout_info)
    
    assert any("无" in i for i in info)
    assert any("右对齐" in i for i in info)


def test_generate_quality_assessment():
    """测试质量评估"""
    generator = AnalysisGenerator()
    
    # 高置信度
    result_high = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.95,
        engine="test",
        processing_time=1.0
    )
    
    assessment_high = generator._generate_quality_assessment(result_high)
    assert isinstance(assessment_high, list)
    assert "质量评估" in assessment_high[0]
    assert any("优秀" in a for a in assessment_high)
    
    # 中等置信度
    result_medium = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.75,
        engine="test",
        processing_time=1.0
    )
    
    assessment_medium = generator._generate_quality_assessment(result_medium)
    assert any("良好" in a for a in assessment_medium)
    
    # 低置信度
    result_low = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.5,
        engine="test",
        processing_time=1.0
    )
    
    assessment_low = generator._generate_quality_assessment(result_low)
    assert any("一般" in a for a in assessment_low)


def test_get_confidence_rating():
    """测试置信度评级"""
    generator = AnalysisGenerator()
    
    # 优秀
    rating_high = generator._get_confidence_rating(0.95)
    assert rating_high["level"] == "优秀"
    assert rating_high["threshold"] == "≥0.9"
    
    # 良好
    rating_medium = generator._get_confidence_rating(0.8)
    assert rating_medium["level"] == "良好"
    assert rating_medium["threshold"] == "0.7-0.9"
    
    # 一般
    rating_low = generator._get_confidence_rating(0.5)
    assert rating_low["level"] == "一般"
    assert rating_low["threshold"] == "<0.7"


def test_get_quality_description():
    """测试质量描述"""
    generator = AnalysisGenerator()
    
    # 高置信度
    result_high = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.95,
        engine="test",
        processing_time=1.0
    )
    
    desc_high = generator._get_quality_description(result_high)
    assert "高" in desc_high
    
    # 中等置信度
    result_medium = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.75,
        engine="test",
        processing_time=1.0
    )
    
    desc_medium = generator._get_quality_description(result_medium)
    assert "中等" in desc_medium
    
    # 低置信度
    result_low = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.5,
        engine="test",
        processing_time=1.0
    )
    
    desc_low = generator._get_quality_description(result_low)
    assert "较低" in desc_low


def test_get_suggestion():
    """测试建议生成"""
    generator = AnalysisGenerator()
    
    # 高置信度
    result_high = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.95,
        engine="test",
        processing_time=1.0
    )
    
    suggestion_high = generator._get_suggestion(result_high)
    assert "可靠" in suggestion_high or "使用" in suggestion_high
    
    # 中等置信度
    result_medium = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.75,
        engine="test",
        processing_time=1.0
    )
    
    suggestion_medium = generator._get_suggestion(result_medium)
    assert "检查" in suggestion_medium
    
    # 低置信度
    result_low = OCRResult(
        text="测试",
        boxes=[],
        confidence=0.5,
        engine="test",
        processing_time=1.0
    )
    
    suggestion_low = generator._get_suggestion(result_low)
    assert "校对" in suggestion_low or "重新" in suggestion_low


def test_generate_analysis_complete():
    """测试完整分析生成"""
    generator = AnalysisGenerator()
    
    result = OCRResult(
        text="这是第一段。\n\n这是第二段。\n\n这是第三段。",
        boxes=[
            BoundingBox(x1=0, y1=0, x2=100, y2=20),
            BoundingBox(x1=0, y1=30, x2=100, y2=50),
            BoundingBox(x1=0, y1=60, x2=100, y2=80)
        ],
        confidence=0.88,
        engine="paddleocr",
        processing_time=2.5
    )
    
    layout_info = {
        "paragraph_count": 3,
        "underline_count": 0,
        "alignment": "left"
    }
    
    analysis = generator.generate_analysis(result, layout_info)
    
    # 验证包含所有部分
    assert "技术解析" in analysis
    assert "文本统计" in analysis
    assert "版式特征" in analysis
    assert "质量评估" in analysis
    assert "paddleocr" in analysis
    assert "3段" in analysis
    assert "0.88" in analysis

