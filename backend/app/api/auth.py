from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import time
from dotenv import load_dotenv
import secrets
from typing import Optional

load_dotenv()

router = APIRouter()

# 从环境变量读取用户名和密码
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# 简单的session存储（生产环境应使用Redis或数据库）
active_sessions = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

@router.post("/login")
async def login(request: LoginRequest):
    """
    用户登录
    """
    if request.username == ADMIN_USERNAME and request.password == ADMIN_PASSWORD:
        # 生成session token
        token = secrets.token_urlsafe(32)
        active_sessions[token] = {
            "username": request.username,
            "login_time": time.time()
        }
        return LoginResponse(
            success=True,
            message="登录成功",
            token=token
        )
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

@router.post("/logout")
async def logout(token: Optional[str] = None):
    """
    用户登出
    """
    if token and token in active_sessions:
        del active_sessions[token]
        return {"success": True, "message": "登出成功"}
    return {"success": True, "message": "已登出"}

@router.get("/check-auth")
async def check_auth(token: Optional[str] = None):
    """
    检查登录状态
    """
    if token and token in active_sessions:
        return {"authenticated": True}
    else:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")

def verify_token(token: str) -> bool:
    """
    验证token是否有效
    """
    return token in active_sessions

