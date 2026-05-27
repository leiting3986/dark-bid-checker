"""暗标格式修复模块"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_LINE_SPACING
from typing import Dict, Any
import copy
from pathlib import Path


class DarkBidFixer:
    """暗标格式修复器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.req = config.get("requirements", {})

    def fix(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """修复文档格式"""
        doc = Document(input_path)
        changes = []

        # 修复页面设置
        changes.extend(self._fix_page_settings(doc))

        # 修复页眉页脚
        changes.extend(self._fix_header_footer(doc))

        # 修复正文格式
        changes.extend(self._fix_text_format(doc))

        # 修复表格格式
        changes.extend(self._fix_table_format(doc))

        # 保存修复后的文档
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path)

        return {
            "success": True,
            "output_path": output_path,
            "total_changes": len(changes),
            "changes": changes,
        }

    def _fix_page_settings(self, doc: Document) -> list:
        """修复页面设置"""
        changes = []
        page_req = self.req.get("page", {})
        margins = page_req.get("margins", {})

        width_mm = page_req.get("width_mm", 210)
        height_mm = page_req.get("height_mm", 297)

        for section in doc.sections:
            section.page_width = Cm(width_mm / 10)
            section.page_height = Cm(height_mm / 10)

            # 设置页边距
            section.top_margin = Cm(margins.get("top_cm", 2.5))
            section.bottom_margin = Cm(margins.get("bottom_cm", 2.5))
            section.left_margin = Cm(margins.get("left_cm", 2.5))
            section.right_margin = Cm(margins.get("right_cm", 2.5))

            changes.append("页面设置: 纸张大小 A4, 页边距 2.5cm")

        return changes

    def _fix_header_footer(self, doc: Document) -> list:
        """修复页眉页脚"""
        changes = []
        page_req = self.req.get("page", {})

        if page_req.get("noHeader", True):
            for section in doc.sections:
                header = section.header
                header.is_linked_to_previous = False
                for para in header.paragraphs:
                    para.clear()
                changes.append("删除页眉")

        if page_req.get("noFooter", True):
            for section in doc.sections:
                footer = section.footer
                footer.is_linked_to_previous = False
                for para in footer.paragraphs:
                    para.clear()
                changes.append("删除页脚")

        return changes

    def _fix_text_format(self, doc: Document) -> list:
        """修复正文格式"""
        changes = []
        text_req = self.req.get("text", {})

        expected_font = text_req.get("font", "宋体")
        expected_size = text_req.get("fontSize_pt", 14)
        expected_color = text_req.get("fontColor", "000000")
        expected_line_spacing = text_req.get("lineSpacing", {}).get("value_pt", 28)

        font_changed = False
        size_changed = False
        color_changed = False
        spacing_changed = False

        for para in doc.paragraphs:
            # 修复段落格式
            pf = para.paragraph_format
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            pf.line_spacing = Pt(expected_line_spacing)
            spacing_changed = True

            # 修复文字格式
            for run in para.runs:
                if run.font.name != expected_font:
                    run.font.name = expected_font
                    font_changed = True

                if run.font.size != Pt(expected_size):
                    run.font.size = Pt(expected_size)
                    size_changed = True

                color_rgb = RGBColor.from_string(expected_color)
                if run.font.color is None or run.font.color.rgb != color_rgb:
                    run.font.color.rgb = color_rgb
                    color_changed = True

        if font_changed:
            changes.append(f"字体: 修改为 {expected_font}")
        if size_changed:
            changes.append(f"字号: 修改为 {expected_size}pt")
        if color_changed:
            changes.append(f"字体颜色: 修改为 #{expected_color}")
        if spacing_changed:
            changes.append(f"段落间距: 段前段后 0pt, 行距 {expected_line_spacing}pt")

        return changes

    def _fix_table_format(self, doc: Document) -> list:
        """修复表格格式"""
        changes = []
        table_req = self.req.get("table", {})

        expected_font = table_req.get("font", "仿宋")
        expected_size = table_req.get("fontSize_pt", 10.5)
        expected_color = table_req.get("fontColor", "000000")

        font_changed = False
        size_changed = False
        color_changed = False

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        for run in para.runs:
                            if run.font.name != expected_font:
                                run.font.name = expected_font
                                font_changed = True

                            if run.font.size != Pt(expected_size):
                                run.font.size = Pt(expected_size)
                                size_changed = True

                            color_rgb = RGBColor.from_string(expected_color)
                            if run.font.color is None or run.font.color.rgb != color_rgb:
                                run.font.color.rgb = color_rgb
                                color_changed = True

        if font_changed:
            changes.append(f"表格字体: 修改为 {expected_font}")
        if size_changed:
            changes.append(f"表格字号: 修改为 {expected_size}pt")
        if color_changed:
            changes.append(f"表格字体颜色: 修改为 #{expected_color}")

        return changes
