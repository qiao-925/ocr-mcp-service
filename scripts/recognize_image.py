"""Recognize text in an image using OCR engines."""

import sys
import json
from pathlib import Path

# Add project root to path before importing scripts.common
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup script environment
from scripts.common import setup_script
setup_script()


def recognize_with_engine(image_path, engine_type="paddleocr", include_analysis=True):
    """Recognize text using specified engine."""
    from ocr_mcp_service.ocr_engine import OCREngineFactory
    from ocr_mcp_service.utils import validate_image
    
    # Validate image
    validate_image(image_path)
    
    # Get engine and recognize
    print(f"Loading {engine_type} engine...")
    engine = OCREngineFactory.get_engine(engine_type)
    print("Recognizing text...")
    result = engine.recognize_image(image_path)
    
    # Remove analysis if not needed
    if not include_analysis:
        result.analysis = None
    
    return result


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OCR image recognition")
    parser.add_argument("image_path", help="Path to image file")
    parser.add_argument(
        "--engine",
        choices=["paddleocr", "paddleocr_mcp", "deepseek"],
        default="paddleocr",
        help="OCR engine to use (default: paddleocr)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="Disable technical analysis in output"
    )
    
    args = parser.parse_args()
    
    # Use absolute path
    image_path = str(Path(args.image_path).resolve())
    
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print("=" * 60)
    print(f"OCR Recognition - {args.engine}")
    print("=" * 60)
    print(f"Image: {image_path}")
    print()
    
    try:
        include_analysis = not args.no_analysis
        result = recognize_with_engine(image_path, args.engine, include_analysis=include_analysis)
        
        if args.json:
            # Output as JSON
            output = result.to_dict()
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            # Human-readable output
            print("\n" + "=" * 60)
            print("Recognition Result")
            print("=" * 60)
            print(f"Engine: {result.engine}")
            print(f"Processing Time: {result.processing_time:.2f}s")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Text Boxes: {len(result.boxes)}")
            print("\nRecognized Text:")
            print("-" * 60)
            # Use get_text_with_analysis() if analysis is enabled, otherwise just text
            if include_analysis and result.analysis:
                print(result.get_text_with_analysis())
            else:
                print(result.text)
            print("-" * 60)
            
            if result.boxes:
                print(f"\nText Boxes ({len(result.boxes)}):")
                for i, box in enumerate(result.boxes[:20], 1):  # Show first 20 boxes
                    print(f"  Box {i}: ({box.x1:.1f}, {box.y1:.1f}) -> ({box.x2:.1f}, {box.y2:.1f})")
                if len(result.boxes) > 20:
                    print(f"  ... and {len(result.boxes) - 20} more boxes")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


