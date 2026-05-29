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
    version="1.0.1",
)

LOCAL_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "http://localhost:3006",
    "http://localhost:3007",
    "http://localhost:3008",
    "http://localhost:3009",
    "http://localhost:3010",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:3005",
    "http://127.0.0.1:3006",
    "http://127.0.0.1:3007",
    "http://127.0.0.1:3008",
    "http://127.0.0.1:3009",
    "http://127.0.0.1:3010",
]

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=LOCAL_ORIGINS,
    allow_credentials=False,
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
