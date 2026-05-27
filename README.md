# 暗标检查工具

检查和修复 Word 文档的暗标格式，确保投标文件符合暗标要求。

## 功能

- **格式检查**: 纸张大小、页边距、字体字号、行距段距、表格格式、禁止内容
- **一键修复**: 自动修复不符合要求的格式
- **配置管理**: 可自定义暗标格式要求

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

## 默认检查项

| 项目 | 要求 |
|------|------|
| 纸张 | A4 (210mm x 297mm) |
| 页边距 | 上下左右 2.5cm |
| 页眉页脚 | 禁止 |
| 正文字体 | 宋体 四号 (14pt) |
| 行距 | 固定值 28 磅 |
| 段间距 | 0 |
| 表格字体 | 仿宋 五号 (10.5pt) |
| 字体颜色 | 黑字白底 |

## 配置文件

配置文件位于 `backend/config/` 目录，JSON 格式，可自行修改暗标要求。

## 技术栈

- **后端**: Python, FastAPI, python-docx
- **前端**: Vue 3, Element Plus, Vite

## 许可证

MIT
