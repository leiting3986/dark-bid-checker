"""核心模块"""
from .config_manager import ConfigManager
from .docx_parser import DocxParser
from .checker import DarkBidChecker
from .fixer import DarkBidFixer

__all__ = ["ConfigManager", "DocxParser", "DarkBidChecker", "DarkBidFixer"]
