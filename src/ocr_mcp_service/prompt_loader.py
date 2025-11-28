"""Prompt template loader and parser."""

import re
from pathlib import Path
from typing import Dict, List, Optional
import importlib.resources


def get_prompt_doc_path() -> Optional[Path]:
    """Get the path to the prompt documentation file."""
    # Try to find the document in multiple locations
    # 1. In the installed package (if packaged)
    try:
        # Try to access via importlib.resources (Python 3.9+)
        with importlib.resources.files("ocr_mcp_service") as package_path:
            # Check if prompt_template.md exists in package root
            template_path = package_path.parent.parent / "prompt_template.md"
            if template_path.exists():
                return template_path
    except Exception:
        pass
    
    # 2. In the project root (development mode)
    # Get the package directory
    try:
        package_path = Path(__file__).parent.parent.parent
        template_path = package_path / "prompt_template.md"
        if template_path.exists():
            return template_path
    except Exception:
        pass
    
    # 3. Try relative to current file
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    template_path = project_root / "prompt_template.md"
    if template_path.exists():
        return template_path
    
    return None


def load_prompt_doc() -> str:
    """Load the prompt documentation file."""
    doc_path = get_prompt_doc_path()
    if doc_path is None:
        raise FileNotFoundError(
            "无法找到Prompt文档。请确保文档已正确安装或位于prompt_template.md"
        )
    
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise IOError(f"无法读取Prompt文档: {e}")


def parse_scenarios(doc_content: str) -> Dict[str, str]:
    """Parse scenarios from the documentation."""
    scenarios = {}
    
    # Pattern to match scenario sections
    # Look for "#### 场景 X：" or "### 场景 X：" followed by scenario name
    # Examples: "#### 场景 1：快速识别" or "#### 场景 2：文档页面分析"
    scenario_pattern = re.compile(
        r'^####\s+场景\s+\d+[：:]\s*(.+?)$', re.MULTILINE
    )
    
    # Find all scenario headers
    matches = list(scenario_pattern.finditer(doc_content))
    
    for i, match in enumerate(matches):
        scenario_name = match.group(1).strip()
        start_pos = match.end()
        
        # Find the end of this scenario (next scenario or next major section)
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            # Last scenario, find next major section (## or ###)
            next_section = re.search(r'^##+\s+', doc_content[start_pos:], re.MULTILINE)
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = len(doc_content)
        
        scenario_content = doc_content[start_pos:end_pos].strip()
        
        # Extract the code block if exists (look for code blocks with or without language)
        code_block_pattern = re.compile(r'```(?:\w+)?\n(.*?)```', re.DOTALL)
        code_match = code_block_pattern.search(scenario_content)
        
        if code_match:
            scenarios[scenario_name] = code_match.group(1).strip()
        else:
            # If no code block, use the full content
            scenarios[scenario_name] = scenario_content
    
    return scenarios


def get_scenario_names() -> List[str]:
    """Get list of available scenario names."""
    return ["通用模板"]


def get_template_file_path() -> Optional[Path]:
    """Get the path to the prompt template file."""
    # Try multiple locations
    try:
        # 1. In the installed package
        with importlib.resources.files("ocr_mcp_service") as package_path:
            template_path = package_path.parent.parent / "prompt_template.md"
            if template_path.exists():
                return template_path
    except Exception:
        pass
    
    # 2. In the project root (development mode)
    try:
        package_path = Path(__file__).parent.parent.parent
        template_path = package_path / "prompt_template.md"
        if template_path.exists():
            return template_path
    except Exception:
        pass
    
    # 3. Try relative to current file
    try:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        template_path = project_root / "prompt_template.md"
        if template_path.exists():
            return template_path
    except Exception:
        pass
    
    return None


def get_scenario_template(scenario_name: str = None) -> str:
    """Get the general prompt template from file."""
    template_path = get_template_file_path()
    if template_path is None:
        raise FileNotFoundError(
            "无法找到Prompt模板文件。请确保文件已正确安装或位于prompt_template.md"
        )
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Try to extract template section if file contains documentation
        # Look for "## 📋 模板内容" or "## 模板内容" section
        template_section_pattern = re.compile(
            r'##+\s*[📋]*\s*模板内容\s*\n(.*?)(?=\n---|\n##|$)', 
            re.DOTALL | re.IGNORECASE
        )
        match = template_section_pattern.search(content)
        
        if match:
            # Extract template content from the section
            template_content = match.group(1).strip()
            if template_content:
                return template_content
        
        # If no section found, check if content starts with template directly
        # (for backward compatibility with simple template files)
        if content.strip().startswith("请分析这张图片") or content.strip().startswith("# 请分析"):
            # Extract content before first "---" separator
            parts = content.split("---", 1)
            if parts and parts[0].strip():
                return parts[0].strip()
        
        # Return entire content if no pattern matches
        content_stripped = content.strip()
        if not content_stripped:
            raise ValueError("Prompt模板文件为空")
        return content_stripped
        
    except FileNotFoundError:
        raise
    except Exception as e:
        raise IOError(f"无法读取Prompt模板文件: {e}")


def get_full_document() -> str:
    """Get the full prompt documentation."""
    return load_prompt_doc()

