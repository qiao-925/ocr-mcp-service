"""Recognize a local image through the simplified OCR service envelope."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for single-image OCR."""
    parser = argparse.ArgumentParser(description="Recognize one local image via Local OCR MCP")
    parser.add_argument("image_path", help="Path to the local image file")
    parser.add_argument("--json", action="store_true", help="Print the full response as JSON")
    return parser


def main() -> int:
    """Run single-image OCR and print either JSON or a readable summary."""
    args = build_argument_parser().parse_args()

    from local_ocr_mcp.services import RecognitionService

    image_path = str(Path(args.image_path).resolve())
    response = RecognitionService().recognize({"path": image_path})

    if args.json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0 if response["status"] == "ok" else 1

    print("=" * 60)
    print("Local OCR MCP")
    print("=" * 60)
    print(f"Image: {image_path}")
    print(f"Status: {response['status']}")

    if response["status"] == "ok":
        data = response["data"]
        assert data is not None
        print(f"Engine: {data['engine']}")
        print(f"Processing: {data['processing_ms']} ms")
        print(f"Confidence: {data['confidence']:.2f}")
        print(f"Boxes: {len(data['boxes'])}")
        print("\nText:")
        print("-" * 60)
        print(data["text"])
        print("-" * 60)
        return 0

    error = response["error"]
    assert error is not None
    print(f"Error: {error['code']}")
    print(error["message"])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
