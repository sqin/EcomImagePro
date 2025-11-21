# EcomImagePro - 电商图片处理工具

一个基于Vue 3和FastAPI的电商图片处理系统，支持图片导入、区域选择、多语言翻译和文本排版功能。

## 功能特性

1. **用户认证** - 简单的用户名密码登录验证，保护系统安全
2. **图片导入** - 支持单张图片上传（后续可扩展批量导入）
3. **区域选择** - 使用矩形框自由选择图片区域
4. **OCR文字识别** - 使用阿里云OCR服务识别选中区域的文字
5. **多语言翻译** - 支持中文、英文、俄文之间的相互翻译
6. **擦除文字** - 使用AI修复技术（inpainting）智能擦除选中区域的文字
7. **添加文字** - 在图片上添加文字，支持矩形区域填充、自动换行、对齐方式
8. **文本排版** - 支持文字大小、字体、颜色设置，自动换行
9. **多语言字体支持** - 自动识别文本语言并加载支持中文、俄文、英文的系统字体
10. **保存图片** - 保存处理后的图片（后续可扩展批量下载）

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
- OpenCV - 图像修复（inpainting）功能，用于清除文字
- 通义千问API (DashScope) - 翻译服务
- 阿里云OCR API - 文字识别服务

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
# 创建 .env 文件，配置以下内容：
# ADMIN_USERNAME=admin          # 登录用户名
# ADMIN_PASSWORD=admin123       # 登录密码（生产环境请修改）
# DASHSCOPE_API_KEY=your_api_key_here  # 通义千问API密钥
# ALIYUN_ACCESS_KEY_ID=your_access_key_id  # 阿里云AccessKey ID
# ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret  # 阿里云AccessKey Secret
```
详细配置说明请参考 `backend/ENV_SETUP.md`

5. 运行后端服务：

**方式一：使用启动脚本（推荐，支持后台运行）**
```bash
# 启动服务（后台运行）
./start.sh

# 停止服务
./stop.sh

# 重启服务
./restart.sh

# 查看日志
tail -f logs/app.log
```

**方式二：直接运行（开发模式）**
```bash
uvicorn app.main:app --reload --port 9000
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
打开浏览器访问 `http://localhost:3000`（或开发服务器显示的地址）

6. 登录系统：
- 首次访问会自动跳转到登录页面
- 使用 `.env` 文件中配置的用户名和密码登录
- 默认用户名：`admin`，默认密码：`admin123`（生产环境请修改）

## API接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/check-auth` - 检查登录状态

### 功能接口（需要认证）
- `POST /api/upload` - 上传图片
- `POST /api/process/ocr` - OCR文字识别
- `POST /api/process/translate-text` - 文本翻译
- `POST /api/erase` - 擦除选中区域的文字（使用AI修复技术）
- `POST /api/add-text` - 添加文字到图片（支持矩形区域填充、自动换行、对齐方式）
- `POST /api/save` - 保存处理后的图片

## 使用说明

1. **登录系统**：首次访问需要输入用户名和密码登录
2. **上传图片**：点击"上传图片"按钮选择要处理的图片
3. **识别与翻译**：
   - 选择"选择区域"操作类型
   - 在图片上拖拽鼠标选择要处理的区域
   - 勾选"识别文字"选项，点击"开始识别"按钮进行OCR识别
   - 识别结果会显示在文本框中
   - 选择源语言和目标语言，点击"执行翻译"按钮
   - 翻译结果会显示在翻译结果框中
4. **擦除文字**：
   - 选择"擦除文字"操作类型
   - 在图片上拖拽鼠标选择要擦除的区域
   - 点击"擦除文字"按钮
   - 系统会使用AI修复技术智能擦除选中区域的文字
   - 擦除后图片编辑区会显示处理后的图片
5. **添加文字**：
   - 选择"添加文字"操作类型
   - 在图片上拖拽鼠标选择文字填充区域
   - 输入文字内容（可以手动输入或复制翻译结果）
   - 设置字体大小、字体类型、文字颜色、对齐方式
   - 点击"添加文字"按钮
   - 文字会在选中的矩形区域内自动换行填充
6. **保存图片**：处理完成后点击"保存图片"按钮下载结果
7. **登出系统**：点击右上角"登出"按钮退出登录

## 注意事项

### 环境配置
- **登录认证**：默认用户名 `admin`，密码 `admin123`，生产环境请务必修改（在 `.env` 文件中配置）
- **API密钥**：需要配置以下密钥才能使用完整功能
  - `DASHSCOPE_API_KEY` - 通义千问API密钥（用于翻译）
  - `ALIYUN_ACCESS_KEY_ID` 和 `ALIYUN_ACCESS_KEY_SECRET` - 阿里云AccessKey（用于OCR识别）
- 详细配置说明请参考 `backend/ENV_SETUP.md`

### 系统要求
- Python 3.8+
- Node.js 16+
- 支持中文、俄文、英文的系统字体（Ubuntu系统可能需要安装中文字体包）

### 使用建议
- 图片处理可能较耗时，请耐心等待
- 建议使用现代浏览器以获得最佳体验
- 收款码图片请放在 `frontend/public/donation/` 目录，例如 `frontend/public/donation/alipay.png`
- 使用 `start.sh` 脚本启动服务时，日志会保存到 `logs/app.log` 文件

### 字体支持
- **macOS**：自动使用 PingFang、STHeiti 等系统字体
- **Windows**：自动使用微软雅黑、宋体、黑体等系统字体
- **Linux/Ubuntu**：需要安装中文字体包
  ```bash
  sudo apt-get install fonts-noto-cjk  # 推荐
  # 或
  sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
  ```

## 开发计划

- [x] 用户登录认证
- [x] OCR文字识别
- [x] 多语言翻译（中文、英文、俄文）
- [x] 擦除文字功能（AI修复技术）
- [x] 添加文字功能（矩形区域填充、自动换行、对齐方式）
- [x] 多语言字体支持（自动识别文本语言）
- [x] 文本自动换行
- [x] 后台运行脚本
- [ ] 批量图片导入功能
- [ ] 批量下载保存功能
- [ ] 更多字体选择
- [ ] 文字位置拖拽调整
- [ ] 撤销/重做功能
- [ ] 图片格式转换
- [ ] Session持久化（Redis/数据库）

## 许可证

MIT License

