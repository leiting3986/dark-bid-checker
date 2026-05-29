"""打包脚本 v1.0.2 - 生成独立 exe，补齐 Word COM 依赖并排除运行文档"""
import PyInstaller.__main__
import os
import shutil
from pathlib import Path

# 清理旧的构建文件
for d in ['build', 'dist']:
    if os.path.exists(d):
        shutil.rmtree(d)

# 准备干净的后端打包目录，避免把上传/输出的历史文档打进 exe
package_backend = Path('build/package_backend/backend')
if package_backend.exists():
    shutil.rmtree(package_backend)
ignore_backend = shutil.ignore_patterns('__pycache__', '*.pyc', 'uploads', 'output')
shutil.copytree('backend', package_backend, ignore=ignore_backend)
(package_backend / 'uploads').mkdir(exist_ok=True)
(package_backend / 'output').mkdir(exist_ok=True)
(package_backend / 'uploads' / '.gitkeep').touch()
(package_backend / 'output' / '.gitkeep').touch()

# 打包参数 - 使用 onedir 模式更稳定
args = [
    'desktop_app.py',
    '--name=暗标检查工具',
    '--onedir',
    '--windowed',
    '--noconfirm',
    '--clean',
    # 添加数据文件
    f'--add-data={package_backend};backend',
    '--add-data=frontend/dist;frontend/dist',
    # 收集完整包
    '--collect-all=docx',
    '--collect-all=lxml',
    '--collect-all=uvicorn',
    '--collect-all=fastapi',
    '--collect-all=starlette',
    '--collect-all=webview',
    '--collect-all=pythoncom',
    '--collect-all=pywintypes',
    '--collect-submodules=win32com',
    # 排除不需要的模块
    '--exclude-module=tkinter',
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
]

print("开始打包...")

PyInstaller.__main__.run(args)

print("\n打包完成！")
print(f"输出目录: dist/暗标检查工具/")
