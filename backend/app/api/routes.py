"""API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import os
import uuid
from pathlib import Path

from ..core import ConfigManager, DarkBidChecker, DarkBidFixer

router = APIRouter()

# 配置管理器
config_manager = ConfigManager(config_dir="config")

# 上传目录
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


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
    try:
        config = config_manager.load_config(config_name)
        return config
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"配置文件不存在: {config_name}")


@router.put("/config/{config_name}")
async def update_config(config_name: str, config: dict):
    """更新配置"""
    path = config_manager.save_config(config, config_name)
    return {"success": True, "path": path}


@router.post("/check")
async def check_document(file: UploadFile = File(...), config_name: Optional[str] = None):
    """检查文档格式"""
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="仅支持 .docx 格式文件")

    # 保存上传文件
    file_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}.docx"

    try:
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)

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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fix")
async def fix_document(file_id: str, config_name: Optional[str] = None):
    """修复文档格式"""
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_id}")
async def download_fixed(file_id: str):
    """下载修复后的文件"""
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
    input_path = UPLOAD_DIR / f"{file_id}.docx"
    output_path = OUTPUT_DIR / f"{file_id}_fixed.docx"

    if input_path.exists():
        input_path.unlink()
    if output_path.exists():
        output_path.unlink()

    return {"success": True}
