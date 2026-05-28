"""FastAPI 主入口"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from app.api.routes import router

app = FastAPI(
    title="暗标检查工具",
    description="检查和修复 Word 文档的暗标格式",
    version="1.0.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


def get_frontend_path():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = str(Path(__file__).parent.parent)
    return os.path.join(base, 'frontend', 'dist')


FRONTEND_DIR = get_frontend_path()


@app.on_event("startup")
async def startup():
    print(f"[启动] 前端目录: {FRONTEND_DIR}")
    print(f"[启动] 目录存在: {os.path.exists(FRONTEND_DIR)}")
    if os.path.exists(FRONTEND_DIR):
        for f in os.listdir(FRONTEND_DIR):
            print(f"[启动] 文件: {f}")


@app.get("/")
async def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({
        "error": "前端文件未找到",
        "frontend_dir": FRONTEND_DIR,
        "exists": os.path.exists(FRONTEND_DIR),
    })


@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    full_path = os.path.join(FRONTEND_DIR, "assets", file_path)
    if os.path.exists(full_path):
        return FileResponse(full_path)
    raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
