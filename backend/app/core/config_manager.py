"""配置管理模块"""
import json
from pathlib import Path
from typing import Optional


class ConfigManager:
    """管理暗标格式要求配置"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config: Optional[dict] = None

    def load_config(self, config_name: str = "default_requirements.json") -> dict:
        """加载配置文件"""
        config_path = self.config_dir / config_name
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = json.load(f)
        return self._config

    def save_config(self, config: dict, config_name: str = "default_requirements.json") -> str:
        """保存配置文件"""
        config_path = self.config_dir / config_name
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self._config = config
        return str(config_path)

    def get_config(self) -> dict:
        """获取当前配置"""
        if self._config is None:
            self.load_config()
        return self._config

    def list_configs(self) -> list:
        """列出所有可用配置"""
        return [f.name for f in self.config_dir.glob("*.json")]
