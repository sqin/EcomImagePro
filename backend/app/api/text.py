from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from PIL import Image, ImageDraw, ImageFont
import uuid

router = APIRouter()

class TextRequest(BaseModel):
    image_id: str
    text: str
    x: int
    y: int
    font_size: int = 24
    font_family: str = "arial.ttf"
    color: str = "#000000"

@router.post("/add-text")
async def add_text(request: TextRequest):
    """
    在图片上添加文字
    """
    try:
        # 查找原始图片
        upload_dir = "uploads"
        image_files = [f for f in os.listdir(upload_dir) if f.startswith(request.image_id)]
        
        if not image_files:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        image_path = os.path.join(upload_dir, image_files[0])
        
        # 打开图片
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            # 尝试使用指定字体
            font_path = request.font_family
            if not os.path.exists(font_path):
                # 如果路径不存在，尝试系统字体
                if os.name == 'nt':  # Windows
                    font_path = "C:/Windows/Fonts/arial.ttf"
                else:  # Linux/Mac
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, request.font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 转换颜色
        color = tuple(int(request.color[i:i+2], 16) for i in (1, 3, 5))
        
        # 绘制文字
        draw.text((request.x, request.y), request.text, fill=color, font=font)
        
        # 保存处理后的图片
        processed_id = str(uuid.uuid4())
        output_path = os.path.join("processed", f"{processed_id}.jpg")
        img.save(output_path, "JPEG", quality=95)
        
        return {
            "processed_id": processed_id,
            "url": f"/processed/{processed_id}.jpg"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加文字失败: {str(e)}")

