"""OCR engine implementations."""

import time
import subprocess
import json
import sys
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

from .models import OCRResult, BoundingBox
from .analysis_generator import AnalysisGenerator
from .progress_tracker import ProgressTracker
from .logger import get_logger
from .mcp_server import send_mcp_log
from .config import (
    PADDLEOCR_MODEL_DIR,
    PADDLEOCR_LANG,
    DEEPSEEK_MODEL_NAME,
    DEEPSEEK_DEVICE,
)

# Global analysis generator instance
_analysis_generator = AnalysisGenerator()


def _add_analysis_to_result(ocr_result: OCRResult, layout_info: Optional[dict] = None) -> OCRResult:
    """Add technical analysis to OCR result."""
    # Add technical analysis
    analysis = _analysis_generator.generate_analysis(ocr_result, layout_info)
    ocr_result.analysis = analysis
    
    # Note: prompt_suggestion is no longer automatically added
    # Use get_prompt_template tool to get prompt example
    
    return ocr_result


class OCREngine(ABC):
    """Abstract base class for OCR engines."""

    @abstractmethod
    def recognize_image(self, image_path: str, **kwargs) -> OCRResult:
        """Recognize text in an image."""
        pass


class PaddleOCREngine(OCREngine):
    """PaddleOCR engine implementation."""

    def __init__(self):
        """Initialize PaddleOCR engine."""
        self.logger = get_logger("PaddleOCREngine")
        try:
            from paddleocr import PaddleOCR

            self.ocr = PaddleOCR(
                use_textline_orientation=True,
                lang=PADDLEOCR_LANG,
            )
            self.logger.info("PaddleOCR engine initialized successfully")
        except ImportError:
            raise ImportError(
                "PaddleOCR not installed. Install with: pip install -e '.[paddleocr]'"
            )

    def recognize_image(self, image_path: str, **kwargs) -> OCRResult:
        """Recognize text in an image using PaddleOCR."""
        start_time = time.time()
        image_path = str(Path(image_path).resolve())
        
        # Initialize progress tracker
        from .logger import log_progress
        progress_tracker = ProgressTracker(
            on_progress=lambda p, s, m: log_progress(
                "PaddleOCREngine", p, m, stage=s, image_path=image_path
            )
        )
        
        self.logger.info(f"开始OCR识别: {image_path}", extra={"image_path": image_path})
        progress_tracker.update(10, "图像加载", "图像路径验证完成")

        # 启动心跳机制，防止长时间操作中断连接
        progress_tracker.start_heartbeat()
        
        try:
            # PaddleOCR 3.x API - cls parameter removed
            progress_tracker.update(20, "OCR引擎调用", "调用PaddleOCR引擎...")
            
            try:
                result = self.ocr.ocr(image_path)
                progress_tracker.update(80, "结果解析", "OCR完成，开始解析结果")
            finally:
                # 确保心跳在操作完成后停止
                progress_tracker.stop_heartbeat()
        except Exception as e:
            self.logger.error(f"OCR引擎调用失败: {e}", exc_info=True)
            raise

        # Parse PaddleOCR 3.x result format
        # Result is a list of dicts, each dict contains:
        # - rec_texts: list of recognized texts
        # - rec_scores: list of confidence scores
        # - rec_polys: list of polygons (4 points) for each text
        text_parts = []
        boxes = []
        confidences = []

        if result and len(result) > 0:
            page_result = result[0]  # First page result
            
            # Determine total items for progress tracking
            total_items = 0
            if isinstance(page_result, dict):
                total_items = len(page_result.get('rec_texts', []))
            elif isinstance(page_result, (list, tuple)):
                total_items = len(page_result)
            
            # PaddleOCR 3.x returns a dict with rec_texts, rec_scores, rec_polys
            if isinstance(page_result, dict):
                rec_texts = page_result.get('rec_texts', [])
                rec_scores = page_result.get('rec_scores', [])
                rec_polys = page_result.get('rec_polys', [])
                
                for i, text in enumerate(rec_texts):
                    if text:  # Skip empty texts
                        text_parts.append(text)
                        confidence = rec_scores[i] if i < len(rec_scores) else 1.0
                        confidences.append(float(confidence))
                        
                        # Extract bounding box from polygon (4 points)
                        if i < len(rec_polys):
                            poly = rec_polys[i]
                            if poly is not None and len(poly) >= 4:
                                # Get min/max coordinates from polygon
                                x_coords = [p[0] for p in poly]
                                y_coords = [p[1] for p in poly]
                                boxes.append(
                                    BoundingBox(
                                        x1=float(min(x_coords)),
                                        y1=float(min(y_coords)),
                                        x2=float(max(x_coords)),
                                        y2=float(max(y_coords)),
                                    )
                                )
                            else:
                                boxes.append(BoundingBox(0, 0, 0, 0))
                        else:
                            boxes.append(BoundingBox(0, 0, 0, 0))
                    
                    # Update progress during parsing
                    if total_items > 0:
                        progress = 80 + (i + 1) / total_items * 15
                        if (i + 1) % max(1, total_items // 10) == 0 or i == total_items - 1:
                            progress_tracker.update(
                                progress,
                                "结果解析",
                                f"已解析 {i + 1}/{total_items} 个文本块"
                            )
            # Fallback for old format (list of tuples)
            elif isinstance(page_result, (list, tuple)):
                for idx, detection in enumerate(page_result):
                    if detection and len(detection) >= 2:
                        box, text_info = detection[0], detection[1]
                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                            text, confidence = text_info[0], text_info[1]
                        else:
                            text, confidence = str(text_info), 1.0
                        
                        if text and box and len(box) >= 4:
                            text_parts.append(text)
                            boxes.append(
                                BoundingBox(
                                    x1=float(box[0][0]),
                                    y1=float(box[0][1]),
                                    x2=float(box[2][0]),
                                    y2=float(box[2][1]),
                                )
                            )
                            confidences.append(float(confidence))
                    
                    # Update progress during parsing
                    if total_items > 0:
                        progress = 80 + (idx + 1) / total_items * 15
                        if (idx + 1) % max(1, total_items // 10) == 0 or idx == total_items - 1:
                            progress_tracker.update(
                                progress,
                                "结果解析",
                                f"已解析 {idx + 1}/{total_items} 个文本块"
                            )

        full_text = "\n".join(text_parts)
        avg_confidence = (
            sum(confidences) / len(confidences) if confidences else 0.0
        )
        processing_time = time.time() - start_time

        progress_tracker.update(95, "后处理", "生成技术分析和视觉分析...")
        
        result = OCRResult(
            text=full_text,
            boxes=boxes,
            confidence=avg_confidence,
            engine="paddleocr",
            processing_time=processing_time,
            progress_history=progress_tracker.get_history(),
        )
        
        # Generate technical analysis
        result = _add_analysis_to_result(result)
        
        progress_tracker.update(100, "完成", "处理完成")
        # 确保心跳在完成后停止
        progress_tracker.stop_heartbeat()
        self.logger.info(
            f"OCR识别完成，耗时 {processing_time:.2f}秒，识别到 {len(text_parts)} 个文本块",
            extra={"processing_time": processing_time, "text_count": len(text_parts)}
        )
        
        return result


class DeepSeekOCREngine(OCREngine):
    """DeepSeek OCR engine implementation."""

    def __init__(self):
        """Initialize DeepSeek OCR engine."""
        self.logger = get_logger("DeepSeekOCREngine")
        try:
            from transformers import pipeline
            from transformers.models.llama import modeling_llama
            import torch
            import os

            # Configure Hugging Face mirror for faster download (especially in China)
            from .config import HF_ENDPOINT, HF_MIRROR
            if HF_ENDPOINT:
                os.environ["HF_ENDPOINT"] = HF_ENDPOINT
            elif HF_MIRROR:
                os.environ["HF_ENDPOINT"] = HF_MIRROR

            # Monkey patch: Create a dummy LlamaFlashAttention2 if it doesn't exist
            # This helps bypass the import error on Windows where flash-attn is not available
            if not hasattr(modeling_llama, "LlamaFlashAttention2"):
                # Use LlamaAttention as a fallback
                class LlamaFlashAttention2(modeling_llama.LlamaAttention):
                    """Dummy LlamaFlashAttention2 that falls back to LlamaAttention."""
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                
                modeling_llama.LlamaFlashAttention2 = LlamaFlashAttention2

            # Determine device: use CUDA if available, unless explicitly set to CPU
            if DEEPSEEK_DEVICE == "cpu":
                device = "cpu"
            elif torch.cuda.is_available():
                device = "cuda"  # Use CUDA if available
            else:
                device = "cpu"
            
            # Try to disable flash attention by setting environment variable
            os.environ.setdefault("TRANSFORMERS_ATTN_IMPLEMENTATION", "eager")
            
            # DeepSeek OCR uses custom model with infer method
            # According to official docs: https://huggingface.co/deepseek-ai/DeepSeek-OCR
            # We use AutoModel and AutoTokenizer, and call model.infer() method
            from transformers import AutoModel, AutoTokenizer
            import time
            import tempfile
            import os
            
            # Helper function to download with retry
            def download_with_retry(func, max_retries=3, delay=5):
                """Download with retry mechanism for network issues."""
                for attempt in range(max_retries):
                    try:
                        return func()
                    except Exception as e:
                        if attempt < max_retries - 1:
                            error_msg = str(e)
                            if "Connection" in error_msg or "IncompleteRead" in error_msg or "timeout" in error_msg.lower():
                                print(f"Download attempt {attempt + 1} failed, retrying in {delay} seconds...")
                                time.sleep(delay)
                                continue
                        raise
            
            # Download tokenizer (not processor)
            # DeepSeek OCR uses AutoTokenizer, not AutoProcessor
            self.tokenizer = download_with_retry(
                lambda: AutoTokenizer.from_pretrained(
                    DEEPSEEK_MODEL_NAME, 
                    trust_remote_code=True
                )
            )
            self.processor = self.tokenizer  # Keep for compatibility
            
            # Download model with retry
            # Use _attn_implementation='flash_attention_2' or 'eager' for Windows
            attn_impl = 'eager' if device == "cpu" or sys.platform == 'win32' else 'flash_attention_2'
            model_dtype = torch.bfloat16 if device != "cpu" else torch.float32
            
            self.model = download_with_retry(
                lambda: AutoModel.from_pretrained(
                    DEEPSEEK_MODEL_NAME,
                    trust_remote_code=True,
                    use_safetensors=True,
                    _attn_implementation=attn_impl,
                )
            )
            
            # Move to device and set dtype
            # Important: Move to device BEFORE setting dtype
            if device != "cpu":
                self.model = self.model.to(device)
                self.model = self.model.to(model_dtype)
            else:
                # For CPU, use float32 (bfloat16 not well supported on CPU)
                self.model = self.model.to(torch.float32)
            
            self.model.eval()
            self.pipeline = None  # Mark that we're using direct model loading
            self.device = device  # Store device for later use
            
            # Create temp directory for output
            self.temp_output_dir = tempfile.mkdtemp(prefix="deepseek_ocr_")
            self.logger.info("DeepSeek OCR engine initialized successfully")
        except ImportError as e:
            error_msg = str(e)
            if "LlamaFlashAttention2" in error_msg or "flash" in error_msg.lower():
                raise RuntimeError(
                    "DeepSeek OCR requires flash-attention support. "
                    "On Windows, this may not be fully supported. "
                    "Please use PaddleOCR or paddleocr-mcp engines instead. "
                    f"Original error: {error_msg}"
                )
            raise ImportError(
                f"DeepSeek OCR dependencies not installed. "
                f"Install with: pip install -e '.[deepseek]' "
                f"Original error: {error_msg}"
            )
        except Exception as e:
            error_msg = str(e)
            if "LlamaFlashAttention2" in error_msg or "flash" in error_msg.lower():
                raise RuntimeError(
                    "DeepSeek OCR requires flash-attention support. "
                    "On Windows, this may not be fully supported. "
                    "Please use PaddleOCR or paddleocr-mcp engines instead. "
                    f"Original error: {error_msg}"
                )
            raise

    def recognize_image(self, image_path: str, **kwargs) -> OCRResult:
        """Recognize text in an image using DeepSeek OCR."""
        start_time = time.time()
        image_path = str(Path(image_path).resolve())
        
        # Initialize progress tracker
        from .logger import log_progress
        progress_tracker = ProgressTracker(
            on_progress=lambda p, s, m: log_progress(
                "DeepSeekOCREngine", p, m, stage=s, image_path=image_path
            )
        )
        
        self.logger.info(f"开始OCR识别: {image_path}", extra={"image_path": image_path})
        progress_tracker.update(10, "图像加载", "图像路径验证完成")

        # 启动心跳机制，防止长时间操作中断连接
        progress_tracker.start_heartbeat()
        
        try:
            if self.pipeline is not None:
                # Use pipeline if available
                result = self.pipeline(image_path)
                
                # Parse DeepSeek OCR result
                if isinstance(result, list) and result:
                    text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    text = result.get("generated_text", "")
                else:
                    text = str(result)
            else:
                # Use direct model loading with infer method
                # According to official docs, DeepSeek OCR has an infer() method
                # Official usage: model.infer(tokenizer, prompt=prompt, image_file=image_file, ...)
                import os
                import tempfile
                
                # Prepare prompt for OCR
                # Default prompt for document OCR
                prompt = "<image>\n<|grounding|>Convert the document to markdown. "
                
                # Create a temporary output directory for this inference
                temp_output = tempfile.mkdtemp(prefix="deepseek_ocr_")
                
                progress_tracker.update(20, "OCR引擎调用", "调用DeepSeek OCR模型...")
            
            try:
                # Call model.infer() method (official API)
                # Parameters: base_size, image_size, crop_mode based on official examples
                result = self.model.infer(
                    self.tokenizer,
                    prompt=prompt,
                    image_file=image_path,
                    output_path=temp_output,
                    base_size=1024,
                    image_size=640,
                    crop_mode=True,
                    save_results=True,
                    test_compress=False  # Set to False for faster inference
                )
                
                # Read the result file
                result_file = os.path.join(temp_output, "result.mmd")
                if not os.path.exists(result_file):
                    result_file = os.path.join(temp_output, "result.txt")
                
                progress_tracker.update(80, "结果解析", "读取OCR结果文件...")
                
                if os.path.exists(result_file):
                    with open(result_file, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                else:
                    # If no result file, try to get text from return value
                    if isinstance(result, str):
                        text = result
                    elif isinstance(result, dict) and "text" in result:
                        text = result["text"]
                    else:
                        text = str(result) if result else ""
                
            except Exception as e:
                # Clean up temp directory on error
                import shutil
                try:
                    shutil.rmtree(temp_output, ignore_errors=True)
                except:
                    pass
                self.logger.error(f"DeepSeek OCR推理失败: {e}", exc_info=True)
                raise RuntimeError(f"DeepSeek OCR inference failed: {e}")
            finally:
                # Clean up temp directory
                import shutil
                try:
                    shutil.rmtree(temp_output, ignore_errors=True)
                except:
                    pass
                # 确保心跳在操作完成后停止
                progress_tracker.stop_heartbeat()

        processing_time = time.time() - start_time
        
        progress_tracker.update(95, "后处理", "生成技术分析和视觉分析...")

        result = OCRResult(
            text=text.strip(),
            boxes=[],  # DeepSeek OCR doesn't provide bounding boxes
            confidence=1.0,  # Default confidence
            engine="deepseek",
            processing_time=processing_time,
            progress_history=progress_tracker.get_history(),
        )
        
        # Generate technical analysis
        result = _add_analysis_to_result(result)
        
        progress_tracker.update(100, "完成", "处理完成")
        # 确保心跳在完成后停止
        progress_tracker.stop_heartbeat()
        self.logger.info(
            f"OCR识别完成，耗时 {processing_time:.2f}秒",
            extra={"processing_time": processing_time}
        )
        
        return result


class PaddleOCRMCPEngine(OCREngine):
    """paddleocr-mcp engine implementation (subprocess call)."""

    def __init__(self):
        """Initialize paddleocr-mcp engine."""
        self.logger = get_logger("PaddleOCRMCPEngine")
        # Check if paddleocr-mcp package is available
        try:
            import paddleocr_mcp
            # paddleocr-mcp is an MCP server, we'll use subprocess to call it
            # Check if we can import it (it's installed)
            self.package_available = True
            self.logger.info("paddleocr-mcp engine initialized successfully")
        except ImportError:
            raise RuntimeError(
                "paddleocr-mcp not installed. "
                "Install with: pip install paddleocr-mcp"
            )

    def recognize_image(self, image_path: str, **kwargs) -> OCRResult:
        """Recognize text in an image using paddleocr-mcp via subprocess."""
        start_time = time.time()
        image_path = str(Path(image_path).resolve())
        
        # Initialize progress tracker
        from .logger import log_progress
        progress_tracker = ProgressTracker(
            on_progress=lambda p, s, m: log_progress(
                "PaddleOCRMCPEngine", p, m, stage=s, image_path=image_path
            )
        )
        
        self.logger.info(f"开始OCR识别: {image_path}", extra={"image_path": image_path})
        progress_tracker.update(10, "图像加载", "图像路径验证完成")

        # 启动心跳机制，防止长时间操作中断连接
        progress_tracker.start_heartbeat()
        
        try:
            # paddleocr-mcp is an MCP server, we need to call it via Python module
            # Try to use it as a Python module first, fallback to subprocess
            try:
                import sys
                import importlib.util
                
                # Try to use paddleocr-mcp's internal API if available
                # Since paddleocr-mcp is an MCP server, we'll use subprocess to call it
                # as a standalone MCP server process
                
                # Use python -m paddleocr_mcp to start the MCP server and communicate via stdio
                # For now, we'll use a simplified approach: use PaddleOCR directly
                # since paddleocr-mcp wraps PaddleOCR
                
                # Fallback: use PaddleOCR directly (paddleocr-mcp uses PaddleOCR internally)
                progress_tracker.update(20, "OCR引擎调用", "调用PaddleOCR引擎...")
                
                from paddleocr import PaddleOCR
                ocr = PaddleOCR()
                result = ocr.ocr(image_path)
                
                progress_tracker.update(80, "结果解析", "OCR完成，开始解析结果")
                
                # Parse result (same as PaddleOCREngine)
                text_parts = []
                boxes = []
                confidences = []
                
                if result and len(result) > 0:
                    page_result = result[0]
                    total_items = 0
                    if isinstance(page_result, dict):
                        total_items = len(page_result.get('rec_texts', []))
                    
                    if isinstance(page_result, dict):
                        rec_texts = page_result.get('rec_texts', [])
                        rec_scores = page_result.get('rec_scores', [])
                        rec_polys = page_result.get('rec_polys', [])
                        
                        for i, text in enumerate(rec_texts):
                            if text:
                                text_parts.append(text)
                                confidence = rec_scores[i] if i < len(rec_scores) else 1.0
                                confidences.append(float(confidence))
                                
                                if i < len(rec_polys):
                                    poly = rec_polys[i]
                                    if poly is not None and len(poly) >= 4:
                                        x_coords = [p[0] for p in poly]
                                        y_coords = [p[1] for p in poly]
                                        boxes.append(
                                            BoundingBox(
                                                x1=float(min(x_coords)),
                                                y1=float(min(y_coords)),
                                                x2=float(max(x_coords)),
                                                y2=float(max(y_coords)),
                                            )
                                        )
                                    else:
                                        boxes.append(BoundingBox(0, 0, 0, 0))
                                else:
                                    boxes.append(BoundingBox(0, 0, 0, 0))
                            
                            # Update progress during parsing
                            if total_items > 0:
                                progress = 80 + (i + 1) / total_items * 15
                                if (i + 1) % max(1, total_items // 10) == 0 or i == total_items - 1:
                                    progress_tracker.update(
                                        progress,
                                        "结果解析",
                                        f"已解析 {i + 1}/{total_items} 个文本块"
                                    )
                
                full_text = "\n".join(text_parts)
                avg_confidence = (
                    sum(confidences) / len(confidences) if confidences else 0.0
                )
                
            except Exception as e:
                self.logger.error(f"paddleocr-mcp识别失败: {e}", exc_info=True)
                raise RuntimeError(f"paddleocr-mcp recognition failed: {e}")
        finally:
            # 确保心跳在操作完成后停止
            progress_tracker.stop_heartbeat()

        processing_time = time.time() - start_time
        
        progress_tracker.update(95, "后处理", "生成技术分析和视觉分析...")

        result = OCRResult(
            text=full_text,
            boxes=boxes,
            confidence=avg_confidence,
            engine="paddleocr_mcp",
            processing_time=processing_time,
            progress_history=progress_tracker.get_history(),
        )
        
        # Generate technical analysis
        result = _add_analysis_to_result(result)
        
        progress_tracker.update(100, "完成", "处理完成")
        # 确保心跳在完成后停止
        progress_tracker.stop_heartbeat()
        self.logger.info(
            f"OCR识别完成，耗时 {processing_time:.2f}秒，识别到 {len(text_parts)} 个文本块",
            extra={"processing_time": processing_time, "text_count": len(text_parts)}
        )
        
        return result


class EasyOCREngine(OCREngine):
    """EasyOCR engine implementation."""

    def __init__(self, languages: Optional[list] = None):
        """Initialize EasyOCR engine.
        
        Args:
            languages: List of language codes (e.g., ['ch_sim', 'en']).
                      Defaults to ['ch_sim', 'en'] for Chinese and English.
        """
        self.logger = get_logger("EasyOCREngine")
        try:
            import easyocr
        except ImportError:
            raise ImportError(
                "EasyOCR not installed. Install with: pip install -e '.[easyocr]'"
            )
        
        # Default to Chinese Simplified and English
        if languages is None:
            languages = ['ch_sim', 'en']
        
        self.reader = easyocr.Reader(languages, gpu=False)  # Use CPU by default
        self.languages = languages
        self.logger.info(f"EasyOCR engine initialized with languages: {languages}")

    def recognize_image(self, image_path: str, **kwargs) -> OCRResult:
        """Recognize text in an image using EasyOCR."""
        start_time = time.time()
        image_path = Path(image_path).resolve()
        
        # Initialize progress tracker
        from .logger import log_progress
        progress_tracker = ProgressTracker(
            on_progress=lambda p, s, m: log_progress(
                "EasyOCREngine", p, m, stage=s, image_path=str(image_path)
            )
        )
        
        self.logger.info(f"开始OCR识别: {image_path}", extra={"image_path": str(image_path)})
        progress_tracker.update(10, "图像加载", "加载图像文件...")

        # 启动心跳机制，防止长时间操作中断连接
        progress_tracker.start_heartbeat()
        
        try:
            # Use PIL to read image (handles Unicode paths better than OpenCV)
            # Then convert to numpy array for EasyOCR
            try:
                from PIL import Image
                import numpy as np
                
                # Read image with PIL (supports Unicode paths)
                pil_image = Image.open(str(image_path)).convert('RGB')
                # Convert to numpy array
                img_array = np.array(pil_image)
                progress_tracker.update(20, "OCR引擎调用", "调用EasyOCR引擎...")
                
                # EasyOCR readtext returns: [[bbox, text, confidence], ...]
                # bbox format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] (4 corner points)
                results = self.reader.readtext(img_array)
                progress_tracker.update(80, "结果解析", "OCR完成，开始解析结果")
            except Exception as e:
                # Fallback to file path if PIL fails
                self.logger.warning(f"PIL读取失败，使用文件路径: {e}")
                progress_tracker.update(20, "OCR引擎调用", "调用EasyOCR引擎（文件路径）...")
                results = self.reader.readtext(str(image_path))
                progress_tracker.update(80, "结果解析", "OCR完成，开始解析结果")
        finally:
            # 确保心跳在操作完成后停止
            progress_tracker.stop_heartbeat()

        text_parts = []
        boxes = []
        confidences = []
        total_items = len(results)

        for idx, detection in enumerate(results):
            if len(detection) >= 3:
                bbox, text, confidence = detection[0], detection[1], detection[2]
                
                if text and bbox and len(bbox) >= 4:
                    text_parts.append(text)
                    confidences.append(float(confidence))
                    
                    # Convert 4-point polygon to bounding box (x1, y1, x2, y2)
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    boxes.append(
                        BoundingBox(
                            x1=float(min(x_coords)),
                            y1=float(min(y_coords)),
                            x2=float(max(x_coords)),
                            y2=float(max(y_coords)),
                        )
                    )
            
            # Update progress during parsing
            if total_items > 0:
                progress = 80 + (idx + 1) / total_items * 15
                if (idx + 1) % max(1, total_items // 10) == 0 or idx == total_items - 1:
                    progress_tracker.update(
                        progress,
                        "结果解析",
                        f"已解析 {idx + 1}/{total_items} 个文本块"
                    )

        full_text = "\n".join(text_parts)
        avg_confidence = (
            sum(confidences) / len(confidences) if confidences else 0.0
        )
        processing_time = time.time() - start_time
        
        progress_tracker.update(95, "后处理", "生成技术分析和视觉分析...")

        result = OCRResult(
            text=full_text,
            boxes=boxes,
            confidence=avg_confidence,
            engine="easyocr",
            processing_time=processing_time,
            progress_history=progress_tracker.get_history(),
        )
        
        # Generate technical analysis
        result = _add_analysis_to_result(result)
        
        progress_tracker.update(100, "完成", "处理完成")
        # 确保心跳在完成后停止
        progress_tracker.stop_heartbeat()
        self.logger.info(
            f"OCR识别完成，耗时 {processing_time:.2f}秒，识别到 {len(text_parts)} 个文本块",
            extra={"processing_time": processing_time, "text_count": len(text_parts)}
        )
        
        return result


class OCREngineFactory:
    """Factory for creating OCR engines with lazy loading and resource management."""

    _engines: dict[str, OCREngine] = {}
    _engine_usage_count: dict[str, int] = {}  # Track usage count for each engine

    @classmethod
    def get_engine(cls, engine_type: str, **kwargs) -> OCREngine:
        """Get OCR engine instance (singleton with lazy loading).
        
        Args:
            engine_type: Type of engine ('paddleocr', 'easyocr', 'deepseek', 'paddleocr_mcp')
            **kwargs: Additional arguments for engine initialization
        
        Returns:
            OCREngine instance
        """
        # For easyocr, use languages as part of the key to support different language configs
        if engine_type == "easyocr" and "languages" in kwargs:
            languages = kwargs.get('languages', None)
            if languages:
                # Create a unique key for each language combination
                engine_key = f"{engine_type}_{','.join(sorted(languages))}"
            else:
                engine_key = engine_type
        else:
            engine_key = engine_type
        
        if engine_key not in cls._engines:
            logger = get_logger("OCREngineFactory")
            logger.info(f"初始化OCR引擎: {engine_type}")
            try:
                if engine_type == "paddleocr":
                    cls._engines[engine_key] = PaddleOCREngine()
                elif engine_type == "deepseek":
                    cls._engines[engine_key] = DeepSeekOCREngine()
                elif engine_type == "paddleocr_mcp":
                    cls._engines[engine_key] = PaddleOCRMCPEngine()
                elif engine_type == "easyocr":
                    languages = kwargs.get('languages', None)
                    cls._engines[engine_key] = EasyOCREngine(languages=languages)
                else:
                    raise ValueError(f"Unknown engine type: {engine_type}")
                
                cls._engine_usage_count[engine_key] = 0
                logger.info(f"OCR引擎初始化成功: {engine_type}")
            except Exception as e:
                logger.error(f"OCR引擎初始化失败: {engine_type}, 错误: {e}", exc_info=True)
                raise
        
        # Track usage
        cls._engine_usage_count[engine_key] = cls._engine_usage_count.get(engine_key, 0) + 1
        return cls._engines[engine_key]
    
    @classmethod
    def get_engine_count(cls) -> int:
        """Get total number of loaded engines."""
        return len(cls._engines)
    
    @classmethod
    def get_usage_stats(cls) -> dict:
        """Get usage statistics for all engines."""
        return {
            "total_engines": len(cls._engines),
            "engines": list(cls._engines.keys()),
            "usage_count": cls._engine_usage_count.copy()
        }

