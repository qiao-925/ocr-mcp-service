"""MCP配置管理模块。

自动检测、生成和更新Cursor MCP配置文件。
"""

import json
import logging
import os
import platform
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MCPConfigManager:
    """MCP配置管理器。

    负责检测Cursor MCP配置文件位置，检查配置，自动生成和更新配置。
    """

    def __init__(self) -> None:
        """初始化配置管理器。"""
        self.config_paths = self._get_config_paths()
        self.project_root = self._get_project_root()

    @staticmethod
    def _get_project_root() -> Path:
        """获取项目根目录。

        Returns:
            项目根目录Path对象
        """
        # 从当前文件位置向上查找，找到包含pyproject.toml的目录
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        # 如果找不到，返回当前目录
        return Path.cwd()

    @staticmethod
    def _get_config_paths() -> list[Path]:
        """获取Cursor MCP配置文件可能的位置。

        Returns:
            配置文件路径列表（按优先级排序）
        """
        system = platform.system()
        config_paths: list[Path] = []

        if system == "Windows":
            # Windows配置路径
            appdata = os.getenv("APPDATA", "")
            userprofile = os.getenv("USERPROFILE", "")
            if appdata:
                config_paths.append(
                    Path(appdata)
                    / "Cursor"
                    / "User"
                    / "globalStorage"
                    / "rooveterinaryinc.roo-cline"
                    / "settings"
                    / "cline_mcp_settings.json"
                )
            if userprofile:
                config_paths.append(Path(userprofile) / ".cursor" / "mcp_settings.json")
                config_paths.append(Path(userprofile) / ".cursor" / "mcp.json")
        elif system == "Darwin":  # macOS
            home = Path.home()
            config_paths.append(
                home
                / "Library"
                / "Application Support"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "rooveterinaryinc.roo-cline"
                / "settings"
                / "cline_mcp_settings.json"
            )
            config_paths.append(home / ".cursor" / "mcp_settings.json")
            config_paths.append(home / ".cursor" / "mcp.json")
        else:  # Linux
            home = Path.home()
            config_paths.append(
                home
                / ".config"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "rooveterinaryinc.roo-cline"
                / "settings"
                / "cline_mcp_settings.json"
            )
            config_paths.append(home / ".cursor" / "mcp_settings.json")
            config_paths.append(home / ".cursor" / "mcp.json")

        return config_paths

    def find_config_file(self) -> Path | None:
        """查找存在的配置文件。

        Returns:
            配置文件路径，如果不存在则返回None
        """
        for config_path in self.config_paths:
            if config_path.exists():
                logger.info(f"找到配置文件: {config_path}")
                return config_path
        return None

    def read_config(self) -> dict[str, Any] | None:
        """读取MCP配置文件。

        Returns:
            配置字典，如果文件不存在或读取失败则返回None
        """
        config_file = self.find_config_file()
        if config_file is None:
            return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"读取配置文件失败: {e}")
            return None

    def write_config(self, config: dict[str, Any]) -> bool:
        """写入MCP配置文件。

        Args:
            config: 配置字典

        Returns:
            是否成功写入
        """
        # 优先使用已存在的配置文件位置，否则使用第一个可能的位置
        config_file = self.find_config_file()
        if config_file is None:
            # 使用第一个可能的位置
            config_file = self.config_paths[0]
            # 确保目录存在
            config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"配置文件已写入: {config_file}")
            return True
        except IOError as e:
            logger.error(f"写入配置文件失败: {e}")
            return False

    def check_ocr_service_config(self) -> dict[str, Any]:
        """检查OCR服务的配置状态。

        Returns:
            包含配置状态的字典：
            - configured: 是否已配置
            - config_file: 配置文件路径
            - service_exists: OCR服务是否存在于配置中
            - current_config: 当前OCR服务配置（如果存在）
            - recommended_config: 推荐配置
        """
        config = self.read_config()
        project_root = self.project_root.resolve()
        venv_python = project_root / ".venv" / "bin" / "python"
        entry_point = project_root / ".venv" / "bin" / "ocr-mcp-server"

        # 检查entry point是否存在
        entry_point_exists = entry_point.exists()
        venv_python_exists = venv_python.exists()

        result: dict[str, Any] = {
            "configured": False,
            "config_file": str(self.find_config_file()) if self.find_config_file() else None,
            "service_exists": False,
            "current_config": None,
            "recommended_config": None,
            "entry_point_exists": entry_point_exists,
            "venv_python_exists": venv_python_exists,
        }

        if config is None:
            # 配置文件不存在，生成推荐配置
            if entry_point_exists:
                result["recommended_config"] = {
                    "command": str(entry_point),
                    "args": [],
                    "env": {},
                }
            elif venv_python_exists:
                result["recommended_config"] = {
                    "command": str(venv_python),
                    "args": ["-m", "ocr_mcp_service"],
                    "env": {},
                }
            return result

        # 检查OCR服务是否已配置
        mcp_servers = config.get("mcpServers", {})
        if "ocr-service" in mcp_servers or "ocr-mcp-service" in mcp_servers:
            service_name = "ocr-service" if "ocr-service" in mcp_servers else "ocr-mcp-service"
            result["configured"] = True
            result["service_exists"] = True
            result["current_config"] = mcp_servers[service_name]

            # 检查配置是否有效
            current_command = mcp_servers[service_name].get("command", "")
            if not Path(current_command).exists():
                result["configured"] = False
                result["config_invalid"] = True
                result["config_error"] = f"配置的命令不存在: {current_command}"

        # 生成推荐配置
        if entry_point_exists:
            result["recommended_config"] = {
                "command": str(entry_point),
                "args": [],
                "env": {},
            }
        elif venv_python_exists:
            result["recommended_config"] = {
                "command": str(venv_python),
                "args": ["-m", "ocr_mcp_service"],
                "env": {},
            }

        return result

    def auto_configure(self, force: bool = False) -> dict[str, Any]:
        """自动配置OCR服务。

        Args:
            force: 是否强制更新现有配置

        Returns:
            配置结果字典：
            - success: 是否成功
            - action: 执行的操作（created/updated/skipped）
            - config_file: 配置文件路径
            - message: 结果消息
        """
        status = self.check_ocr_service_config()
        project_root = self.project_root.resolve()

        # 检查entry point是否存在
        entry_point = project_root / ".venv" / "bin" / "ocr-mcp-server"
        venv_python = project_root / ".venv" / "bin" / "python"

        if not entry_point.exists() and not venv_python.exists():
            return {
                "success": False,
                "action": "skipped",
                "message": "未找到可执行文件，请先运行: uv pip install -e .",
                "config_file": None,
            }

        # 读取或创建配置
        config = self.read_config()
        if config is None:
            config = {"mcpServers": {}}

        # 检查是否需要更新
        service_name = "ocr-service"
        if not force and service_name in config.get("mcpServers", {}):
            current_config = config["mcpServers"][service_name]
            current_command = current_config.get("command", "")
            if Path(current_command).exists():
                return {
                    "success": True,
                    "action": "skipped",
                    "message": "配置已存在且有效，无需更新",
                    "config_file": str(self.find_config_file()),
                }

        # 生成配置
        if entry_point.exists():
            service_config = {
                "command": str(entry_point),
                "args": [],
                "env": {},
            }
        else:
            service_config = {
                "command": str(venv_python),
                "args": ["-m", "ocr_mcp_service"],
                "env": {},
            }

        # 更新配置
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        config["mcpServers"][service_name] = service_config

        # 写入配置
        if self.write_config(config):
            action = "updated" if status["service_exists"] else "created"
            return {
                "success": True,
                "action": action,
                "message": f"配置已{action}",
                "config_file": str(self.find_config_file() or self.config_paths[0]),
            }
        else:
            return {
                "success": False,
                "action": "failed",
                "message": "写入配置文件失败",
                "config_file": None,
            }

    def get_config_info(self) -> dict[str, Any]:
        """获取配置信息（用于MCP工具）。

        Returns:
            配置信息字典
        """
        status = self.check_ocr_service_config()
        project_root = self.project_root.resolve()

        info: dict[str, Any] = {
            "project_root": str(project_root),
            "config_status": status,
            "possible_config_paths": [str(p) for p in self.config_paths],
            "entry_point_path": str(project_root / ".venv" / "bin" / "ocr-mcp-server"),
            "venv_python_path": str(project_root / ".venv" / "bin" / "python"),
            "entry_point_exists": (project_root / ".venv" / "bin" / "ocr-mcp-server").exists(),
            "venv_python_exists": (project_root / ".venv" / "bin" / "python").exists(),
        }

        return info

