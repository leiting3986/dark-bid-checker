# 暗标检查工具

检查和修复 Word 文档的暗标格式，确保投标文件符合暗标要求。

## 功能

- **格式检查**: 纸张大小、页边距、字体字号、行距段距、表格格式、页眉页脚、页码、禁止内容、电子签章
- **一键修复**: 自动修复不符合要求的格式，合格文档不会误报修改
- **配置管理**: 内置默认配置，可自定义暗标格式要求
- **一键导入**: 从文本自动解析格式要求并应用
- **纸张支持**: A3/A4/B5 选择自动同步宽高

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+

### 启动

```bash
# 1. 启动后端
cd backend
pip install -r requirements.txt
python main.py

# 2. 启动前端 (新终端)
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 桌面应用

```bash
# pywebview 桌面版
pip install pywebview uvicorn
python desktop_app.py

# 或运行 start-desktop.bat
```

## 默认检查项

| 项目 | 要求 |
|------|------|
| 纸张 | A4 (210mm x 297mm) |
| 页边距 | 上下左右 2.5cm |
| 页眉页脚 | 禁止 |
| 页码 | 禁止 |
| 正文字体 | 宋体 四号 (14pt) |
| 行距 | 固定值 28 磅 |
| 段间距 | 0 |
| 表格字体 | 仿宋 五号 (10.5pt) |
| 字体颜色 | 黑字白底 |

## 配置

配置文件位于 `backend/config/` 目录，JSON 格式。可通过前端界面编辑，也支持从文本一键导入。"恢复默认"按钮会重置为内置默认配置。

## 技术栈

- **后端**: Python, FastAPI, python-docx
- **前端**: Vue 3, Element Plus, Vite
- **桌面**: Electron / pywebview

## 许可证

MIT
