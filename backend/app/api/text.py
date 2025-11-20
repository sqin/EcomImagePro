from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from PIL import Image, ImageDraw, ImageFont
import uuid
import cv2
import numpy as np
import platform

router = APIRouter()

def get_unicode_font(font_size: int):
    """
    获取支持多语言的字体（中文、俄文、英文等）
    """
    system = platform.system()
    
    # macOS 字体路径（支持中文、俄文、英文）
    mac_fonts = [
        "/System/Library/Fonts/PingFang.ttc",  # 支持中文
        "/System/Library/Fonts/STHeiti Light.ttc",  # 支持中文
        "/System/Library/Fonts/STHeiti Medium.ttc",  # 支持中文
        "/Library/Fonts/Arial Unicode.ttf",  # 支持中文、俄文、英文
        "/System/Library/Fonts/Helvetica.ttc",  # 支持俄文、英文
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # 备用路径
    ]
    
    # Windows 字体路径（支持中文、俄文、英文）
    windows_fonts = [
        "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑 - 支持中文、俄文、英文
        "C:/Windows/Fonts/msyhbd.ttc",    # 微软雅黑 Bold
        "C:/Windows/Fonts/simhei.ttf",    # 黑体 - 支持中文
        "C:/Windows/Fonts/simsun.ttc",     # 宋体 - 支持中文
        "C:/Windows/Fonts/arial.ttf",     # Arial - 支持俄文、英文
        "C:/Windows/Fonts/arialuni.ttf",  # Arial Unicode - 支持多语言
        "C:/Windows/Fonts/times.ttf",     # Times New Roman - 支持俄文、英文
    ]
    
    # Linux 字体路径（支持中文、俄文、英文）
    linux_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # 支持俄文、英文
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 支持中文
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",    # 支持中文
        "/usr/share/fonts/truetype/arphic/uming.ttc",      # 支持中文
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # 支持俄文、英文
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # 支持中文
    ]
    
    font_paths = []
    if system == "Darwin":  # macOS
        font_paths = mac_fonts
    elif system == "Windows":
        font_paths = windows_fonts
    else:  # Linux
        font_paths = linux_fonts
    
    # 尝试加载字体
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                # 如果是 .ttc 文件，需要指定索引
                if font_path.endswith('.ttc'):
                    return ImageFont.truetype(font_path, font_size, index=0)
                else:
                    return ImageFont.truetype(font_path, font_size)
            except:
                continue
    
    # 如果都失败，返回默认字体
    return ImageFont.load_default()

def wrap_text(text: str, font, max_width: int):
    """
    将文本按最大宽度换行
    """
    lines = []
    words = text.split('\n')  # 先按换行符分割
    
    for line in words:
        if not line:
            lines.append('')
            continue
            
        # 检查是否需要换行
        words_in_line = []
        current_line = ''
        
        for char in line:
            test_line = current_line + char
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
    
    return lines

class Region(BaseModel):
    x: int
    y: int
    width: int
    height: int

class TextRequest(BaseModel):
    image_id: str
    text: str
    x: int
    y: int
    font_size: int = 24
    font_family: str = "arial.ttf"
    color: str = "#000000"
    region: Optional[Region] = None

@router.post("/add-text")
async def add_text(request: TextRequest):
    """
    在图片上添加文字
    """
    try:
        # 查找图片（先在processed目录查找，再在uploads目录查找）
        image_path = None
        
        # 先检查processed目录（处理后的图片）
        processed_dir = "processed"
        if os.path.exists(processed_dir):
            # 精确匹配：{image_id}.jpg
            exact_match = os.path.join(processed_dir, f"{request.image_id}.jpg")
            if os.path.exists(exact_match):
                image_path = exact_match
            else:
                # 模糊匹配：以image_id开头的文件
                processed_files = [f for f in os.listdir(processed_dir) if f.startswith(request.image_id)]
                if processed_files:
                    image_path = os.path.join(processed_dir, processed_files[0])
        
        # 如果processed目录没找到，再检查uploads目录（原始图片）
        if not image_path:
            upload_dir = "uploads"
            if os.path.exists(upload_dir):
                # 模糊匹配：以image_id开头的文件（原始上传的文件名可能包含更多字符）
                image_files = [f for f in os.listdir(upload_dir) if f.startswith(request.image_id)]
                if image_files:
                    image_path = os.path.join(upload_dir, image_files[0])
        
        if not image_path or not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail=f"图片不存在 (image_id: {request.image_id})")
        
        # 打开图片
        img = Image.open(image_path).convert("RGB")

        # 如果提供了region参数，先清除区域内的文字
        if request.region:
            # 将PIL Image转换为numpy array供OpenCV使用
            img_np = np.array(img)

            # 创建掩码，标记需要修复的区域（白色区域表示需要修复）
            mask = np.zeros((img_np.shape[0], img_np.shape[1]), dtype=np.uint8)
            region = request.region
            mask[region.y:region.y + region.height, region.x:region.x + region.width] = 255

            # 使用OpenCV的inpainting功能清除文字
            # INPAINT_TELEA算法适用于大多数场景
            inpainted = cv2.inpaint(img_np, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

            # 将处理后的numpy array转回PIL Image
            img = Image.fromarray(inpainted)

        draw = ImageDraw.Draw(img)
        
        # 加载字体（优先使用支持中文的字体）
        try:
            # 尝试使用指定字体
            font_path = request.font_family
            if os.path.exists(font_path):
                if font_path.endswith('.ttc'):
                    font = ImageFont.truetype(font_path, request.font_size, index=0)
                else:
                    font = ImageFont.truetype(font_path, request.font_size)
            else:
                # 使用支持多语言（中文、俄文、英文）的系统字体
                font = get_unicode_font(request.font_size)
        except Exception as e:
            # 如果加载失败，使用支持多语言（中文、俄文、英文）的系统字体
            font = get_unicode_font(request.font_size)
        
        # 转换颜色
        color = tuple(int(request.color[i:i+2], 16) for i in (1, 3, 5))
        
        # 确定文本区域宽度（如果有region，使用region宽度；否则使用图片宽度减去x坐标）
        if request.region:
            max_width = request.region.width
        else:
            max_width = img.width - request.x - 10  # 留10像素边距
        
        # 文本换行处理
        text_lines = wrap_text(request.text, font, max_width)
        
        # 计算行高（根据文本类型选择合适的测试字符）
        # 检测文本类型：中文、俄文或其他
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in request.text)
        has_russian = any('\u0400' <= c <= '\u04FF' for c in request.text)
        
        if has_chinese:
            test_char = "中"  # 中文字符
        elif has_russian:
            test_char = "А"  # 俄文字符（西里尔字母A）
        else:
            test_char = "A"  # 英文字符
        
        bbox = font.getbbox(test_char)
        line_height = bbox[3] - bbox[1] + 5  # 行高加5像素间距
        
        # 绘制多行文字
        y_offset = request.y
        for line in text_lines:
            if line:  # 只绘制非空行
                draw.text((request.x, y_offset), line, fill=color, font=font)
            # 无论是否为空行，都增加行高（保持空行间距）
            y_offset += line_height
        
        # 保存处理后的图片
        processed_id = str(uuid.uuid4())
        output_path = os.path.join("processed", f"{processed_id}.jpg")
        img.save(output_path, "JPEG", quality=95)
        
        return {
            "processed_id": processed_id,
            "url": f"/processed/{processed_id}.jpg"
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        import traceback
        error_detail = f"添加文字失败: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # 打印详细错误信息到控制台
        raise HTTPException(status_code=500, detail=f"添加文字失败: {str(e)}")

