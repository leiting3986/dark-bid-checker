"""暗标格式检查核心模块"""
from typing import Dict, List, Any
from .docx_parser import DocxParser
import re


class CheckResult:
    """检查结果"""

    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.passed: List[str] = []

    def add_error(self, category: str, message: str, detail: str = "", location: str = ""):
        self.errors.append({
            "level": "error",
            "category": category,
            "message": message,
            "detail": detail,
            "location": location,
        })

    def add_warning(self, category: str, message: str, detail: str = "", location: str = ""):
        self.warnings.append({
            "level": "warning",
            "category": category,
            "message": message,
            "detail": detail,
            "location": location,
        })

    def add_passed(self, check_name: str):
        self.passed.append(check_name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "total_passed": len(self.passed),
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "passed": self.passed,
        }


class DarkBidChecker:
    """暗标格式检查器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.req = config.get("requirements", {})

    def check(self, file_path: str) -> Dict[str, Any]:
        """执行完整检查"""
        parser = DocxParser(file_path)
        result = CheckResult()

        # 检查页面设置
        self._check_page_settings(parser, result)

        # 检查页眉页脚
        self._check_header_footer(parser, result)

        # 检查正文格式
        self._check_text_format(parser, result)

        # 检查表格格式
        self._check_table_format(parser, result)

        # 检查图片
        self._check_images(parser, result)

        # 检查禁止内容
        self._check_forbidden_content(parser, result)

        return result.to_dict()

    def _check_page_settings(self, parser: DocxParser, result: CheckResult):
        """检查页面设置"""
        page_req = self.req.get("page", {})
        settings = parser.get_page_settings()

        # 检查纸张大小
        expected_width = page_req.get("width_mm", 210)
        expected_height = page_req.get("height_mm", 297)
        tolerance = 2  # 允许 2mm 误差

        width_ok = abs(settings["page_width_mm"] - expected_width) <= tolerance
        height_ok = abs(settings["page_height_mm"] - expected_height) <= tolerance

        if width_ok and height_ok:
            result.add_passed("纸张大小: A4")
        else:
            result.add_error(
                "页面设置",
                "纸张大小不符合要求",
                f"当前: {settings['page_width_mm']:.0f}mm x {settings['page_height_mm']:.0f}mm, 要求: A4 ({expected_width}mm x {expected_height}mm)",
                "页面设置"
            )

        # 检查页边距
        margins = page_req.get("margins", {})
        margin_checks = [
            ("上边距", settings["margin_top_cm"], margins.get("top_cm", 2.5)),
            ("下边距", settings["margin_bottom_cm"], margins.get("bottom_cm", 2.5)),
            ("左边距", settings["margin_left_cm"], margins.get("left_cm", 2.5)),
            ("右边距", settings["margin_right_cm"], margins.get("right_cm", 2.5)),
        ]

        for name, actual, expected in margin_checks:
            if actual is None:
                result.add_error("页面设置", f"{name}未设置", "", "页面设置")
            elif abs(actual - expected) > 0.1:
                result.add_error(
                    "页面设置",
                    f"{name}不符合要求",
                    f"当前: {actual:.2f}cm, 要求: {expected}cm",
                    "页面设置"
                )
            else:
                result.add_passed(f"{name}: {expected}cm")

    def _check_header_footer(self, parser: DocxParser, result: CheckResult):
        """检查页眉页脚"""
        page_req = self.req.get("page", {})
        settings = parser.get_page_settings()

        if page_req.get("noHeader", True):
            if settings["has_header"]:
                result.add_error("页面设置", "文档包含页眉", "暗标不得包含页眉", "页眉")
            else:
                result.add_passed("无页眉")

        if page_req.get("noFooter", True):
            if settings["has_footer"]:
                result.add_error("页面设置", "文档包含页脚", "暗标不得包含页脚", "页脚")
            else:
                result.add_passed("无页脚")

    def _check_text_format(self, parser: DocxParser, result: CheckResult):
        """检查正文格式"""
        text_req = self.req.get("text", {})
        paragraphs = parser.get_paragraphs_info()

        expected_font = text_req.get("font", "宋体")
        expected_size = text_req.get("fontSize_pt", 14)
        expected_color = text_req.get("fontColor", "000000")
        expected_spacing = text_req.get("paragraphSpacing_pt", 0)
        expected_line_spacing = text_req.get("lineSpacing", {}).get("value_pt", 28)

        font_errors = []
        size_errors = []
        color_errors = []
        spacing_errors = []

        for para in paragraphs:
            if not para["runs"]:
                continue

            location = f"段落 {para['index'] + 1}: {para['text'][:20]}..."

            # 检查段间距
            pf = para["paragraph_format"]
            if pf["space_before_pt"] and abs(pf["space_before_pt"] - expected_spacing) > 1:
                spacing_errors.append(f"段前间距: {pf['space_before_pt']:.1f}pt")
            if pf["space_after_pt"] and abs(pf["space_after_pt"] - expected_spacing) > 1:
                spacing_errors.append(f"段后间距: {pf['space_after_pt']:.1f}pt")

            # 检查行间距
            if pf["line_spacing"] is not None and pf["line_spacing_rule"] == "exact":
                if abs(pf["line_spacing"] - expected_line_spacing) > 1:
                    spacing_errors.append(f"行间距: {pf['line_spacing']:.1f}pt (要求: {expected_line_spacing}pt)")

            for run in para["runs"]:
                # 检查字体
                if run["font_name"] and run["font_name"] != expected_font:
                    font_errors.append(f"字体: {run['font_name']} (位置: {location})")

                # 检查字号
                if run["font_size_pt"] and abs(run["font_size_pt"] - expected_size) > 0.5:
                    size_errors.append(f"字号: {run['font_size_pt']}pt (位置: {location})")

                # 检查颜色
                if run["font_color"] and run["font_color"] != expected_color:
                    color_errors.append(f"颜色: #{run['font_color']} (位置: {location})")

        if font_errors:
            result.add_error(
                "正文格式",
                f"字体不符合要求 (共 {len(font_errors)} 处)",
                f"要求: {expected_font}, " + "; ".join(font_errors[:5]),
                "正文"
            )
        else:
            result.add_passed(f"字体: {expected_font}")

        if size_errors:
            result.add_error(
                "正文格式",
                f"字号不符合要求 (共 {len(size_errors)} 处)",
                f"要求: {expected_size}pt, " + "; ".join(size_errors[:5]),
                "正文"
            )
        else:
            result.add_passed(f"字号: {expected_size}pt")

        if color_errors:
            result.add_error(
                "正文格式",
                f"字体颜色不符合要求 (共 {len(color_errors)} 处)",
                f"要求: #{expected_color}, " + "; ".join(color_errors[:5]),
                "正文"
            )
        else:
            result.add_passed(f"字体颜色: #{expected_color}")

        if spacing_errors:
            result.add_warning(
                "正文格式",
                f"段落间距可能不符合要求",
                "; ".join(spacing_errors[:5]),
                "正文"
            )
        else:
            result.add_passed("段落间距")

    def _check_table_format(self, parser: DocxParser, result: CheckResult):
        """检查表格格式"""
        table_req = self.req.get("table", {})
        tables = parser.get_tables_info()

        if not tables:
            result.add_passed("无表格")
            return

        expected_font = table_req.get("font", "仿宋")
        expected_size = table_req.get("fontSize_pt", 10.5)
        expected_color = table_req.get("fontColor", "000000")

        font_errors = []
        size_errors = []
        color_errors = []

        for table in tables:
            for cell in table["cells"]:
                location = f"表格 {table['index'] + 1}, 行 {cell['row'] + 1}, 列 {cell['col'] + 1}"

                for para in cell["paragraphs"]:
                    for run in para["runs"]:
                        if run["font_name"] and run["font_name"] != expected_font:
                            font_errors.append(f"{location}: {run['font_name']}")

                        if run["font_size_pt"] and abs(run["font_size_pt"] - expected_size) > 0.5:
                            size_errors.append(f"{location}: {run['font_size_pt']}pt")

                        if run["font_color"] and run["font_color"] != expected_color:
                            color_errors.append(f"{location}: #{run['font_color']}")

        if font_errors:
            result.add_error(
                "表格格式",
                f"表格字体不符合要求 (共 {len(font_errors)} 处)",
                f"要求: {expected_font}, " + "; ".join(font_errors[:5]),
                "表格"
            )
        else:
            result.add_passed(f"表格字体: {expected_font}")

        if size_errors:
            result.add_error(
                "表格格式",
                f"表格字号不符合要求 (共 {len(size_errors)} 处)",
                f"要求: {expected_size}pt, " + "; ".join(size_errors[:5]),
                "表格"
            )
        else:
            result.add_passed(f"表格字号: {expected_size}pt")

        if color_errors:
            result.add_error(
                "表格格式",
                f"表格字体颜色不符合要求 (共 {len(color_errors)} 处)",
                f"要求: #{expected_color}, " + "; ".join(color_errors[:5]),
                "表格"
            )
        else:
            result.add_passed(f"表格字体颜色: #{expected_color}")

    def _check_images(self, parser: DocxParser, result: CheckResult):
        """检查图片"""
        if parser.has_images():
            result.add_warning(
                "图片",
                "文档包含图片",
                "请确保图片为电脑绘制，白底黑字，文字采用仿宋五号",
                "文档"
            )
        else:
            result.add_passed("无图片")

    def _check_forbidden_content(self, parser: DocxParser, result: CheckResult):
        """检查禁止内容"""
        forbidden = self.req.get("forbiddenContent", {})
        full_text = parser.get_all_text()

        # 检查投标人名称
        for name in forbidden.get("bidderNames", []):
            if name and name in full_text:
                result.add_error(
                    "禁止内容",
                    f"发现投标人名称: {name}",
                    "暗标中不得出现投标人名称",
                    "文档内容"
                )

        # 检查企业名称
        for name in forbidden.get("companyNames", []):
            if name and name in full_text:
                result.add_error(
                    "禁止内容",
                    f"发现企业名称: {name}",
                    "暗标中不得出现可识别投标人身份的企业名称",
                    "文档内容"
                )

        # 检查自定义模式
        for pattern in forbidden.get("customPatterns", []):
            if pattern:
                matches = re.findall(pattern, full_text)
                if matches:
                    result.add_error(
                        "禁止内容",
                        f"发现禁止内容: {pattern}",
                        f"匹配到: {', '.join(matches[:5])}",
                        "文档内容"
                    )

        if not any(forbidden.get(k) for k in ["bidderNames", "companyNames", "customPatterns"]):
            result.add_passed("禁止内容检查 (未配置禁止词)")
