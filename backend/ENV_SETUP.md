# 环境变量配置说明

## 创建 .env 文件

在 `backend` 目录下创建 `.env` 文件，内容如下：

```
# 登录认证配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# 阿里云OCR服务配置
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# 通义千问API密钥（用于翻译）
DASHSCOPE_API_KEY=your_api_key_here
```

## 登录认证配置

- `ADMIN_USERNAME`: 登录用户名（默认: admin）
- `ADMIN_PASSWORD`: 登录密码（默认: admin123）

**重要提示**：生产环境请务必修改默认的用户名和密码！

## 获取阿里云AccessKey

1. 访问 [阿里云控制台](https://home.console.aliyun.com/)
2. 进入"访问控制" -> "用户" -> "创建用户"
3. 创建AccessKey，获取 AccessKey ID 和 AccessKey Secret
4. 确保该用户有OCR服务的权限
5. 将 AccessKey ID 和 AccessKey Secret 复制到 `.env` 文件中

## 获取通义千问API密钥

1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建API密钥
4. 将密钥复制到 `.env` 文件中的 `DASHSCOPE_API_KEY` 字段

## 服务说明

本项目使用以下阿里云服务：
- **OCR文字识别**：使用阿里云OCR API服务进行图片文字识别
- **文本翻译**：使用通义千问模型 (qwen-turbo) 进行文本翻译

无需额外安装OCR软件或配置其他服务。

