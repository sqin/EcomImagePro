from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from datetime import datetime

router = APIRouter()

class SaveRequest(BaseModel):
    processed_id: str
    filename: Optional[str] = None

@router.post("/save")
async def save_image(request: SaveRequest):
    """
    保存处理后的图片
    """
    try:
        processed_path = os.path.join("processed", f"{request.processed_id}.jpg")
        
        if not os.path.exists(processed_path):
            raise HTTPException(status_code=404, detail="处理后的图片不存在")
        
        # 如果指定了文件名，复制到downloads目录
        if request.filename:
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            download_path = os.path.join(downloads_dir, request.filename)
            shutil.copy2(processed_path, download_path)
            return {
                "message": "保存成功",
                "filename": request.filename,
                "url": f"/downloads/{request.filename}"
            }
        else:
            # 直接返回文件用于下载
            return FileResponse(
                processed_path,
                media_type="image/jpeg",
                filename=f"processed_{request.processed_id}.jpg"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

