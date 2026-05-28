"""配置管理模块"""
import copy
import json
from pathlib import Path
from typing import Optional


PAGE_SIZE_MAP = {
    "A3": {"width_mm": 297, "height_mm": 420},
    "A4": {"width_mm": 210, "height_mm": 297},
    "A5": {"width_mm": 148, "height_mm": 210},
    "B5": {"width_mm": 176, "height_mm": 250},
}

BUILTIN_DEFAULT_CONFIG = {
    "version": "1.0",
    "name": "技术标暗标要求",
    "requirements": {
        "signature": {
            "enabled": True,
            "description": "不得对'暗标'文件进行电子签章或上传带有签章的扫描页",
        },
        "page": {
            "size": "A4",
            "width_mm": 210,
            "height_mm": 297,
            "margins": {
                "top_cm": 2.5,
                "bottom_cm": 2.5,
                "left_cm": 2.5,
                "right_cm": 2.5,
            },
            "noHeader": True,
            "noFooter": True,
            "noPageNumber": True,
        },
        "text": {
            "font": "宋体",
            "fontSize_pt": 14,
            "fontSize_name": "四号",
            "fontColor": "000000",
            "backgroundColor": "FFFFFF",
            "paragraphSpacing_pt": 0,
            "lineSpacing": {
                "type": "exact",
                "value_pt": 28,
            },
        },
        "table": {
            "font": "仿宋",
            "fontSize_pt": 10.5,
            "fontSize_name": "五号",
            "fontColor": "000000",
            "backgroundColor": "FFFFFF",
        },
        "image": {
            "mustBeComputerDrawn": True,
            "backgroundColor": "FFFFFF",
            "fontColor": "000000",
        },
        "forbiddenContent": {
            "bidderNames": [],
            "companyNames": [],
            "projectNames": [],
            "identifiers": [],
            "customPatterns": [],
        },
    },
}


class ConfigManager:
    """管理暗标格式要求配置"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config: Optional[dict] = None

    @staticmethod
    def normalize_config(config: dict) -> dict:
        """规范化配置中可由名称推导的字段"""
        req = config.setdefault("requirements", {})
        page = req.setdefault("page", {})
        size = str(page.get("size", "A4")).upper()
        if size in PAGE_SIZE_MAP:
            page["size"] = size
            page.update(PAGE_SIZE_MAP[size])
        return config

    @staticmethod
    def builtin_default() -> dict:
        """获取内置默认配置副本"""
        return copy.deepcopy(BUILTIN_DEFAULT_CONFIG)

    def load_config(self, config_name: str = "default_requirements.json") -> dict:
        """加载配置文件"""
        config_path = self.config_dir / config_name
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = self.normalize_config(json.load(f))
        return self._config

    def save_config(self, config: dict, config_name: str = "default_requirements.json") -> str:
        """保存配置文件"""
        config = self.normalize_config(config)
        config_path = self.config_dir / config_name
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self._config = config
        return str(config_path)

    def reset_to_builtin_default(self, config_name: str = "default_requirements.json") -> dict:
        """恢复内置默认配置"""
        config = self.builtin_default()
        self.save_config(config, config_name)
        return config

    def get_config(self) -> dict:
        """获取当前配置"""
        if self._config is None:
            self.load_config()
        return self._config

    def list_configs(self) -> list:
        """列出所有可用配置"""
        return [f.name for f in self.config_dir.glob("*.json")]
