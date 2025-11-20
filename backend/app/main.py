from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import upload, process, text, save

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

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(process.router, prefix="/api/process", tags=["process"])
app.include_router(text.router, prefix="/api", tags=["text"])
app.include_router(save.router, prefix="/api", tags=["save"])

@app.get("/")
async def root():
    return {"message": "EcomImagePro API"}

