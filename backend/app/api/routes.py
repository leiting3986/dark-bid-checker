"""API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import re
import uuid
from pathlib import Path

from ..core import ConfigManager, DarkBidChecker, DarkBidFixer, doc_to_docx, is_doc_file
from ..core import parse_requirements, apply_parsed_config, get_parsed_fields_text

router = APIRouter()

# 配置管理器
config_manager = ConfigManager(config_dir="config")

# 使用绝对路径
BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 文件大小限制 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# UUID 格式校验
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def validate_file_id(file_id: str) -> str:
    """校验 file_id 格式，防止路径遍历"""
    if not UUID_PATTERN.match(file_id):
        raise HTTPException(status_code=400, detail="无效的文件 ID")
    return file_id


def validate_config_name(config_name: str) -> str:
    """校验配置文件名，防止路径遍历"""
    if not re.match(r'^[a-zA-Z0-9_\-一-龥]+\.json$', config_name):
        raise HTTPException(status_code=400, detail="无效的配置文件名")
    return config_name


@router.get("/configs")
async def list_configs():
    """列出所有可用配置"""
    return {
        "configs": config_manager.list_configs(),
        "current": config_manager.get_config().get("name", ""),
    }


@router.get("/config/{config_name}")
async def get_config(config_name: str):
    """获取指定配置"""
    validate_config_name(config_name)
    try:
        config = config_manager.load_config(config_name)
        return config
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"配置文件不存在: {config_name}")


@router.put("/config/{config_name}")
async def update_config(config_name: str, config: dict):
    """更新配置"""
    validate_config_name(config_name)
    # 基本结构验证
    if "requirements" not in config:
        raise HTTPException(status_code=400, detail="配置必须包含 requirements 字段")
    path = config_manager.save_config(config, config_name)
    return {"success": True, "path": path}


@router.post("/check")
async def check_document(file: UploadFile = File(...), config_name: Optional[str] = None):
    """检查文档格式"""
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".docx") or filename_lower.endswith(".doc")):
        raise HTTPException(status_code=400, detail="仅支持 .doc 和 .docx 格式文件")

    # 文件大小检查
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)")

    file_id = str(uuid.uuid4())
    original_path = UPLOAD_DIR / f"{file_id}_original{Path(file.filename).suffix}"
    input_path = UPLOAD_DIR / f"{file_id}.docx"

    try:
        # 保存原始文件
        with open(original_path, "wb") as f:
            f.write(content)

        # 如果是 .doc 格式，转换为 .docx
        if is_doc_file(file.filename):
            try:
                doc_to_docx(str(original_path), str(UPLOAD_DIR))
                # 转换后的文件名基于 file_id
                converted_path = UPLOAD_DIR / f"{file_id}_original.docx"
                if converted_path.exists():
                    converted_path.rename(input_path)
                else:
                    raise HTTPException(status_code=500, detail="doc 转换失败")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"doc 转换失败: {str(e)}")
        else:
            # .docx 直接重命名
            original_path.rename(input_path)

        # 加载配置
        if config_name:
            config = config_manager.load_config(config_name)
        else:
            config = config_manager.get_config()

        # 执行检查
        checker = DarkBidChecker(config)
        result = checker.check(str(input_path))

        return {
            "success": True,
            "filename": file.filename,
            "file_id": file_id,
            "result": result,
        }

    except Exception as e:
        # 清理文件
        if input_path.exists():
            input_path.unlink()
        raise HTTPException(status_code=500, detail="检查失败，请确认文件格式正确")


@router.post("/fix/{file_id}")
async def fix_document(file_id: str, config_name: Optional[str] = None):
    """修复文档格式"""
    validate_file_id(file_id)
    input_path = UPLOAD_DIR / f"{file_id}.docx"

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在，请先上传检查")

    try:
        # 加载配置
        if config_name:
            config = config_manager.load_config(config_name)
        else:
            config = config_manager.get_config()

        # 执行修复
        output_path = OUTPUT_DIR / f"{file_id}_fixed.docx"
        fixer = DarkBidFixer(config)
        result = fixer.fix(str(input_path), str(output_path))

        return {
            "success": True,
            "file_id": file_id,
            "result": result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="修复失败，请确认文件格式正确")


@router.get("/download/{file_id}")
async def download_fixed(file_id: str):
    """下载修复后的文件"""
    validate_file_id(file_id)
    file_path = OUTPUT_DIR / f"{file_id}_fixed.docx"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="修复后的文件不存在")

    return FileResponse(
        path=str(file_path),
        filename=f"fixed_{file_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.delete("/cleanup/{file_id}")
async def cleanup_files(file_id: str):
    """清理临时文件"""
    validate_file_id(file_id)
    input_path = UPLOAD_DIR / f"{file_id}.docx"
    output_path = OUTPUT_DIR / f"{file_id}_fixed.docx"

    if input_path.exists():
        input_path.unlink()
    if output_path.exists():
        output_path.unlink()

    return {"success": True}


@router.post("/config/import")
async def import_config(data: dict):
    """从文本解析配置"""
    text = data.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="请输入配置文本")

    parsed = parse_requirements(text)
    if not parsed:
        raise HTTPException(status_code=400, detail="未能识别任何配置项，请检查输入格式")

    fields = get_parsed_fields_text(parsed)
    return {
        "success": True,
        "parsed": parsed,
        "fields": fields,
    }
