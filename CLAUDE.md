# 暗标检查工具

检查和修复 Word 文档的暗标格式。

## 项目结构

```
暗标识别/
├── backend/          # Python FastAPI 后端
│   ├── main.py       # 入口
│   ├── config/       # 配置文件
│   ├── uploads/      # 上传文件
│   ├── output/       # 修复后文件
│   └── app/
│       ├── core/     # 核心逻辑 (解析/检查/修复)
│       └── api/      # API 路由
├── frontend/         # Vue 3 + Element Plus 前端
│   └── src/
│       ├── components/
│       └── utils/
```

## 启动命令

```bash
# 后端 (端口 8000)
cd backend && python main.py

# 前端 (端口 3000)
cd frontend && npm run dev
```

## 技术栈

- 后端: Python 3.14, FastAPI, python-docx
- 前端: Vue 3, Element Plus, Vite, Axios

## 核心功能

1. 检查 Word 文档格式 (纸张/页边距/字体/行距/表格/禁止内容)
2. 一键修复格式问题
3. 可配置暗标要求

## 开发规范

- Python: 中文注释
- Vue: Composition API
- 提交信息: 中文
