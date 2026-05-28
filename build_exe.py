"""打包脚本 - 生成独立 exe"""
import PyInstaller.__main__
import os
import shutil

# 清理旧的构建文件
for d in ['build', 'dist']:
    if os.path.exists(d):
        shutil.rmtree(d)

# 打包参数 - 使用 onedir 模式更稳定
args = [
    'desktop_app.py',
    '--name=暗标检查工具',
    '--onedir',
    '--windowed',
    '--noconfirm',
    '--clean',
    # 添加数据文件
    '--add-data=backend;backend',
    '--add-data=frontend/dist;frontend/dist',
    # 收集完整包
    '--collect-all=docx',
    '--collect-all=lxml',
    '--collect-all=uvicorn',
    '--collect-all=fastapi',
    '--collect-all=starlette',
    '--collect-all=webview',
    # 排除不需要的模块
    '--exclude-module=tkinter',
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
]

print("开始打包...")

PyInstaller.__main__.run(args)

print("\n打包完成！")
print(f"输出目录: dist/暗标检查工具/")
