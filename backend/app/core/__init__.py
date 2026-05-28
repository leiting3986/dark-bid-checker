"""核心模块"""
from .config_manager import ConfigManager
from .docx_parser import DocxParser
from .checker import DarkBidChecker
from .fixer import DarkBidFixer
from .converter import doc_to_docx, is_doc_file
from .config_parser import parse_requirements, apply_parsed_config, get_parsed_fields_text

__all__ = ["ConfigManager", "DocxParser", "DarkBidChecker", "DarkBidFixer", "doc_to_docx", "is_doc_file",
           "parse_requirements", "apply_parsed_config", "get_parsed_fields_text"]
