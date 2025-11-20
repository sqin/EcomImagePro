from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from PIL import Image
from app.services.translation import translate_text
from app.services.ocr import extract_text_from_region

router = APIRouter()

class Region(BaseModel):
    x: int
    y: int
    width: int
    height: int

class OCRRequest(BaseModel):
    image_id: str
    region: Region

class TranslateRequest(BaseModel):
    image_id: str
    region: Region
    source_lang: str  # 'zh', 'en', 'ru'
    target_lang: str  # 'zh', 'en', 'ru'

class TranslateTextRequest(BaseModel):
    text: str
    source_lang: str  # 'zh', 'en', 'ru'
    target_lang: str  # 'zh', 'en', 'ru'

@router.post("/ocr")
async def recognize_text(request: OCRRequest):
    """
    识别选中区域的文字（OCR）
    """
    try:
        # 查找原始图片
        upload_dir = "uploads"
        image_files = [f for f in os.listdir(upload_dir) if f.startswith(request.image_id)]
        
        if not image_files:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        image_path = os.path.join(upload_dir, image_files[0])
        
        # 打开图片
        img = Image.open(image_path)
        
        # 提取选中区域的图片
        region = request.region
        roi = img.crop((region.x, region.y, region.x + region.width, region.y + region.height))
        
        # OCR识别文字
        text, temp_image_path = extract_text_from_region(roi, image_path, region)
        
        # 构建临时图片的访问URL
        temp_image_url = None
        if temp_image_path:
            temp_image_url = f"/temp_ocr/{os.path.basename(temp_image_path)}"
        
        return {
            "text": text,
            "temp_image_url": temp_image_url,
            "temp_image_path": temp_image_path,
            "region": {
                "x": region.x,
                "y": region.y,
                "width": region.width,
                "height": region.height
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")

@router.post("/translate")
async def translate_region(request: TranslateRequest):
    """
    翻译选中区域的文字
    """
    try:
        # 查找原始图片
        upload_dir = "uploads"
        image_files = [f for f in os.listdir(upload_dir) if f.startswith(request.image_id)]
        
        if not image_files:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        image_path = os.path.join(upload_dir, image_files[0])
        
        # 打开图片
        img = Image.open(image_path)
        
        # 提取选中区域的图片
        region = request.region
        roi = img.crop((region.x, region.y, region.x + region.width, region.y + region.height))
        
        # OCR识别文字
        text, temp_image_path = extract_text_from_region(roi, image_path, region)
        
        if not text:
            return {
                "text": "",
                "translated_text": "",
                "message": "未识别到文字",
                "temp_image_url": f"/temp_ocr/{os.path.basename(temp_image_path)}" if temp_image_path else None
            }
        
        # 调用翻译服务
        translated_text = translate_text(text, request.source_lang, request.target_lang)
        
        # 构建临时图片的访问URL
        temp_image_url = None
        if temp_image_path:
            temp_image_url = f"/temp_ocr/{os.path.basename(temp_image_path)}"
        
        return {
            "text": text,
            "translated_text": translated_text,
            "temp_image_url": temp_image_url,
            "region": {
                "x": region.x,
                "y": region.y,
                "width": region.width,
                "height": region.height
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")

@router.post("/translate-text")
async def translate_text_from_text(request: TranslateTextRequest):
    """
    使用已识别的文字进行翻译
    """
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="文本内容不能为空")

        translated_text = translate_text(text, request.source_lang, request.target_lang)
        return {
            "text": text,
            "translated_text": translated_text
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")

