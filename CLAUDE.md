# 暗标检查工具

检查和修复 Word 文档的暗标格式。

## 项目结构

```
暗标识别/
├── backend/              # Python FastAPI 后端
│   ├── main.py           # 入口
│   ├── config/           # 配置文件
│   ├── uploads/          # 上传文件
│   ├── output/           # 修复后文件
│   └── app/
│       ├── core/         # 核心逻辑
│       │   ├── config_manager.py  # 配置管理 (含内置默认、normalize)
│       │   ├── config_parser.py   # 文本配置解析
│       │   ├── docx_parser.py     # Word 文档解析 (多节/页码/样式回退)
│       │   ├── checker.py         # 格式检查
│       │   ├── fixer.py           # 格式修复
│       │   └── converter.py       # doc 转 docx
│       └── api/          # API 路由
├── frontend/             # Vue 3 + Element Plus 前端
│   ├── src/
│   │   ├── components/
│   │   │   └── ConfigEditor.vue   # 配置编辑 (纸张尺寸同步/一键导入)
│   │   └── utils/
│   │       └── api.js            # Axios 封装
│   └── electron/
│       └── main.js               # Electron 入口 (自动启动后端)
├── desktop_app.py        # pywebview 桌面入口
├── build_exe.py          # PyInstaller 打包脚本
└── start-desktop.bat     # Windows 桌面启动脚本
```

## 启动命令

```bash
# 后端 (端口 8000)
cd backend && python main.py

# 前端 (端口 3000)
cd frontend && npm run dev

# 桌面应用 (pywebview)
python desktop_app.py
```

## 技术栈

- 后端: Python 3.9+, FastAPI, python-docx
- 前端: Vue 3, Element Plus, Vite, Axios
- 桌面: Electron 或 pywebview

## 核心功能

1. 检查 Word 文档格式 (纸张/页边距/字体/行距/表格/页眉页脚/页码/禁止内容)
2. 一键修复格式问题 (文档合格时不会误报修改)
3. 可配置暗标要求 (内置默认配置 + 用户自定义)
4. 一键导入配置 (从文本自动解析格式要求)
5. 纸张 A3/A4/B5 选择自动同步宽高

## 开发规范

- Python: 中文注释
- Vue: Composition API
- 提交信息: 中文
