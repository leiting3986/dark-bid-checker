"""配置需求文本解析模块"""
import re
from typing import Dict, Any, List

# 字号名 → pt 映射
FONT_SIZE_MAP = {
    "初号": 42, "小初": 36,
    "一号": 26, "小一": 24,
    "二号": 22, "小二": 18,
    "三号": 16, "小三": 15,
    "四号": 14, "小四": 12,
    "五号": 10.5, "小五": 9,
    "六号": 7.5, "小六": 6.5,
    "七号": 5.5, "八号": 5,
}

FONT_SIZE_REVERSE = {v: k for k, v in FONT_SIZE_MAP.items()}


def parse_requirements(text: str) -> Dict[str, Any]:
    """解析文本，返回配置增量"""
    result = {}
    unmatched = []

    # 纸张大小
    m = re.search(r'(A[345]|B5)', text, re.IGNORECASE)
    if m:
        size = m.group(1).upper()
        result["page.size"] = size

    # 页边距
    margin_patterns = [
        # "页边距上下2.5cm，左右3cm" 或 "上下2.5cm，左右3cm"
        (r'上[下下]?\s*(\d+\.?\d*)\s*cm', "tb"),
        (r'左[右]?\s*(\d+\.?\d*)\s*cm', "lr"),
        # "页边距2.5cm" 统一值
        (r'(?:页边距|边距)\s*(\d+\.?\d*)\s*cm', "all"),
        # "上2.5 下2.5 左3 右3"
        (r'上\s*(\d+\.?\d*)', "top"),
        (r'下\s*(\d+\.?\d*)', "bottom"),
        (r'左\s*(\d+\.?\d*)', "left"),
        (r'右\s*(\d+\.?\d*)', "right"),
    ]

    margins = {}
    for pattern, key in margin_patterns:
        m = re.search(pattern, text)
        if m:
            val = float(m.group(1))
            if key == "tb":
                margins["top"] = val
                margins["bottom"] = val
            elif key == "lr":
                margins["left"] = val
                margins["right"] = val
            elif key == "all":
                margins = {"top": val, "bottom": val, "left": val, "right": val}
            else:
                margins[key] = val

    if margins:
        if "top" in margins:
            result["page.margins.top_cm"] = margins["top"]
        if "bottom" in margins:
            result["page.margins.bottom_cm"] = margins["bottom"]
        if "left" in margins:
            result["page.margins.left_cm"] = margins["left"]
        if "right" in margins:
            result["page.margins.right_cm"] = margins["right"]

    # 正文字体
    font_match = re.search(r'正文?\s*(宋体|仿宋|黑体|楷体)', text)
    if font_match:
        result["text.font"] = font_match.group(1)

    # 正文字号
    size_match = re.search(r'正文?\s*(?:宋体|仿宋|黑体|楷体)?\s*(初号|小初|一号|小一|二号|小二|三号|小三|四号|小四|五号|小五|六号|小六|七号|八号)', text)
    if size_match:
        name = size_match.group(1)
        result["text.fontSize_pt"] = FONT_SIZE_MAP[name]
        result["text.fontSize_name"] = name

    # 行距
    line_match = re.search(r'行距\s*(\d+\.?\d*)\s*磅', text)
    if line_match:
        result["text.lineSpacing.value_pt"] = float(line_match.group(1))

    # 段间距
    para_match = re.search(r'段[前后间距]*\s*(\d+\.?\d*)\s*磅', text)
    if para_match:
        result["text.paragraphSpacing_pt"] = float(para_match.group(1))

    # 表格字体
    table_font_match = re.search(r'表格\s*(宋体|仿宋|黑体|楷体)', text)
    if table_font_match:
        result["table.font"] = table_font_match.group(1)

    # 表格字号
    table_size_match = re.search(r'表格\s*(?:宋体|仿宋|黑体|楷体)?\s*(初号|小初|一号|小一|二号|小二|三号|小三|四号|小四|五号|小五|六号|小六|七号|八号)', text)
    if table_size_match:
        name = table_size_match.group(1)
        result["table.fontSize_pt"] = FONT_SIZE_MAP[name]
        result["table.fontSize_name"] = name

    # 页眉页脚
    if re.search(r'(禁止|不得|不要|不允许|无)\s*页眉', text):
        result["page.noHeader"] = True
    if re.search(r'(禁止|不得|不要|不允许|无)\s*页脚', text):
        result["page.noFooter"] = True

    # 投标人名称
    bidder_match = re.search(r'投标人\s*名?\s*称?\s*[：:]\s*(.+)', text)
    if bidder_match:
        name = bidder_match.group(1).strip()
        result["forbiddenContent.bidderNames"] = [n.strip() for n in re.split(r'[,，、;；\s]+', name) if n.strip()]

    return result


def apply_parsed_config(config: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    """将解析结果应用到配置"""
    req = config.setdefault("requirements", {})

    for key, value in parsed.items():
        parts = key.split(".")
        target = req
        for part in parts[:-1]:
            if part == "margins":
                target = target.setdefault("margins", {})
            elif part == "lineSpacing":
                target = target.setdefault("lineSpacing", {})
            elif part == "forbiddenContent":
                target = target.setdefault("forbiddenContent", {})
            else:
                target = target.setdefault(part, {})
        target[parts[-1]] = value

    return config


def get_parsed_fields_text(parsed: Dict[str, Any]) -> List[str]:
    """将解析结果转为可读文本列表"""
    labels = {
        "page.size": "纸张大小",
        "page.margins.top_cm": "上边距",
        "page.margins.bottom_cm": "下边距",
        "page.margins.left_cm": "左边距",
        "page.margins.right_cm": "右边距",
        "page.noHeader": "禁止页眉",
        "page.noFooter": "禁止页脚",
        "text.font": "正文字体",
        "text.fontSize_pt": "正文字号",
        "text.lineSpacing.value_pt": "行距",
        "text.paragraphSpacing_pt": "段间距",
        "table.font": "表格字体",
        "table.fontSize_pt": "表格字号",
        "forbiddenContent.bidderNames": "禁止内容",
    }
    result = []
    for key, value in parsed.items():
        label = labels.get(key, key)
        if key == "text.fontSize_pt":
            name = FONT_SIZE_REVERSE.get(value, "")
            result.append(f"{label}: {name}({value}pt)")
        elif key == "text.lineSpacing.value_pt":
            result.append(f"{label}: {value}磅")
        elif isinstance(value, bool):
            result.append(f"{label}: {'是' if value else '否'}")
        elif isinstance(value, list):
            result.append(f"{label}: {', '.join(value)}")
        else:
            result.append(f"{label}: {value}")
    return result
