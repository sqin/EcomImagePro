from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片接口
    返回图片ID和访问URL
    """
    # 检查文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="文件必须是图片格式")
    
    # 生成唯一ID
    image_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1] or '.jpg'
    filename = f"{image_id}{file_extension}"
    filepath = os.path.join("uploads", filename)
    
    # 保存文件
    try:
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return JSONResponse({
            "image_id": image_id,
            "filename": filename,
            "url": f"/uploads/{filename}",
            "size": len(content)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

