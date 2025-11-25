"""配置管理模块。

定义默认配置和配置加载逻辑。
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class OCRConfig:
    """OCR服务配置类。

    Attributes:
        use_angle_cls: 是否使用角度分类
        lang: 识别语言（ch=中文，en=英文等）
        log_dir: 日志目录
        log_file: 日志文件路径
        log_level: 日志级别
    """

    def __init__(
        self,
        use_angle_cls: bool = True,
        lang: str = "ch",
        log_dir: Path | str | None = None,
        log_level: int = logging.INFO,
    ) -> None:
        """初始化配置。

        Args:
            use_angle_cls: 是否使用角度分类，默认True
            lang: 识别语言，默认'ch'（中文）
            log_dir: 日志目录，默认None（使用项目根目录下的logs）
            log_level: 日志级别，默认INFO
        """
        self.use_angle_cls = use_angle_cls
        self.lang = lang

        # 设置日志目录
        if log_dir is None:
            # 默认使用项目根目录下的logs目录
            project_root = Path(__file__).parent.parent.parent
            self.log_dir = project_root / "logs"
        else:
            self.log_dir = Path(log_dir)

        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "mcp_ocr_server.log"
        self.log_level = log_level

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式。

        Returns:
            配置字典
        """
        return {
            "use_angle_cls": self.use_angle_cls,
            "lang": self.lang,
            "log_dir": str(self.log_dir),
            "log_file": str(self.log_file),
            "log_level": self.log_level,
        }


# 默认配置实例
default_config = OCRConfig()

