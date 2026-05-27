"""doc 转 docx 转换模块"""
import os
import pythoncom
import win32com.client
from pathlib import Path
from typing import Optional


def doc_to_docx(doc_path: str, output_dir: Optional[str] = None) -> str:
    """将 .doc 文件转换为 .docx

    Args:
        doc_path: .doc 文件路径
        output_dir: 输出目录，默认与输入文件同目录

    Returns:
        转换后的 .docx 文件路径
    """
    doc_path = Path(doc_path).resolve()
    if not doc_path.exists():
        raise FileNotFoundError(f"文件不存在: {doc_path}")

    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = doc_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    docx_path = output_dir / f"{doc_path.stem}.docx"

    # 初始化 COM
    pythoncom.CoInitialize()
    word = None
    doc = None

    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False

        doc = word.Documents.Open(str(doc_path))
        doc.SaveAs(str(docx_path), FileFormat=16)  # 16 = wdFormatXMLDocument (docx)
        doc.Close()

        return str(docx_path)

    finally:
        if doc:
            try:
                doc.Close()
            except Exception:
                pass
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


def is_doc_file(filename: str) -> bool:
    """检查文件是否为 .doc 格式"""
    return filename.lower().endswith('.doc') and not filename.lower().endswith('.docx')
