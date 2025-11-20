# EcomImagePro - 电商图片处理工具

一个基于Vue 3和FastAPI的电商图片处理系统，支持图片导入、区域选择、多语言翻译和文本排版功能。

## 功能特性

1. **图片导入** - 支持单张图片上传（后续可扩展批量导入）
2. **区域选择** - 使用矩形框自由选择图片区域
3. **操作类型**：
   - **翻译** - 支持中文-英文、中文-俄文、英文-俄文翻译（使用阿里云OCR识别文字）
   - **添加文字** - 在图片上添加文字，支持自定义样式
4. **文本排版** - 支持文字大小、位置、字体设置
5. **保存图片** - 保存处理后的图片（后续可扩展批量下载）

## 技术栈

### 前端
- Vue 3 (Composition API)
- Element Plus UI组件库
- Axios (HTTP请求)
- Canvas API (图片绘制和区域选择)
- Vite (构建工具)

### 后端
- FastAPI
- Pillow (PIL) - 图片处理
- 通义千问API (DashScope) - 翻译服务和OCR识别

## 项目结构

```
EcomImagePro/
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── api/           # API调用
│   │   └── utils/         # 工具函数
│   └── package.json
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── main.py        # 入口文件
│   └── requirements.txt
└── README.md
```

## 安装和运行

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
# 创建 .env 文件，填入通义千问API密钥
# DASHSCOPE_API_KEY=your_api_key_here
```
详细配置说明请参考 `backend/ENV_SETUP.md`

5. 运行后端服务：
```bash
uvicorn app.main:app --reload --port 8000
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 运行开发服务器：
```bash
npm run dev
```

4. 访问应用：
打开浏览器访问 `http://localhost:3000`

## API接口

- `POST /api/upload` - 上传图片
- `POST /api/process/translate` - 翻译选中区域文字（自动OCR识别）
- `POST /api/add-text` - 添加文字到图片
- `POST /api/save` - 保存处理后的图片
- `POST /api/process/translate-text` - 使用已识别文字直接翻译（无需再次OCR）

## 使用说明

1. **上传图片**：点击"上传图片"按钮选择要处理的图片
2. **选择区域**：在图片上拖拽鼠标选择要处理的区域
3. **选择操作**：
   - **翻译**：选择"翻译"操作，选择源语言和目标语言，点击"执行翻译"（系统会自动识别选中区域的文字）
   - **添加文字**：选择"添加文字"操作，输入文字内容，设置样式（大小、字体、颜色），点击"添加文字"
4. **保存图片**：处理完成后点击"保存图片"按钮下载结果

## 注意事项

- 通义千问API需要配置API Key（在`.env`文件中设置`DASHSCOPE_API_KEY`）
- OCR识别和翻译功能都使用阿里云DashScope服务，需要同一个API Key
- 收款码图片请放在 `frontend/public/donation/` 目录，例如 `frontend/public/donation/alipay.png`
- 图片处理可能较耗时，请耐心等待
- 建议使用现代浏览器以获得最佳体验

## 开发计划

- [ ] 批量图片导入功能
- [ ] 批量下载保存功能
- [ ] 更多字体选择
- [ ] 文字位置拖拽调整
- [ ] 撤销/重做功能
- [ ] 图片格式转换

## 许可证

MIT License

