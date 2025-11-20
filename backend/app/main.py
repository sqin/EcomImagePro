from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.api import upload, process, text, save, auth

app = FastAPI(title="EcomImagePro API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
os.makedirs("downloads", exist_ok=True)
os.makedirs("temp_ocr", exist_ok=True)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/processed", StaticFiles(directory="processed"), name="processed")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
app.mount("/temp_ocr", StaticFiles(directory="temp_ocr"), name="temp_ocr")

# 注册路由（auth路由不需要认证）
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# 不需要认证的路径
PUBLIC_PATHS = ["/api/auth/login", "/api/auth/check-auth", "/"]

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    认证中间件：保护需要认证的API
    """
    path = request.url.path
    
    # 跳过不需要认证的路径
    if any(path.startswith(public_path) for public_path in PUBLIC_PATHS):
        response = await call_next(request)
        return response
    
    # 跳过静态文件
    if path.startswith(("/uploads/", "/processed/", "/downloads/", "/temp_ocr/")):
        response = await call_next(request)
        return response
    
    # 检查token
    token = request.headers.get("Authorization")
    if not token:
        # 尝试从查询参数获取
        token = request.query_params.get("token")
    
    if token:
        # 移除 "Bearer " 前缀（如果有）
        if token.startswith("Bearer "):
            token = token[7:]
        
        # 验证token
        if auth.verify_token(token):
            response = await call_next(request)
            return response
    
    # 未认证
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "需要登录"}
    )

# 注册需要认证的路由
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(process.router, prefix="/api/process", tags=["process"])
app.include_router(text.router, prefix="/api", tags=["text"])
app.include_router(save.router, prefix="/api", tags=["save"])

@app.get("/")
async def root():
    return {"message": "EcomImagePro API"}

