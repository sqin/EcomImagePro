from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from PIL import Image, ImageDraw, ImageFont
import uuid
import cv2
import numpy as np
import platform
import subprocess

router = APIRouter()

def find_chinese_fonts_linux():
    """
    在Linux系统上使用fc-list查找支持中文的字体
    """
    chinese_fonts = []
    try:
        # 使用fc-list查找支持中文的字体
        result = subprocess.run(
            ['fc-list', ':lang=zh', 'file'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # fc-list输出格式: /path/to/font.ttf: FontName:style=...
                    font_path = line.split(':')[0].strip()
                    if os.path.exists(font_path):
                        chinese_fonts.append(font_path)
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return chinese_fonts

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
    linux_fonts_static = [
        # Noto字体（Google开发，广泛支持中文）
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.otf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttf",
        # 文泉驿字体
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 支持中文
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",    # 支持中文
        "/usr/share/fonts/truetype/wqy/wqy-microhei/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei/wqy-zenhei.ttc",
        # 文鼎字体
        "/usr/share/fonts/truetype/arphic/uming.ttc",      # 支持中文
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
        # DejaVu字体（支持俄文、英文）
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        # Liberation字体（支持俄文、英文）
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    
    font_paths = []
    if system == "Darwin":  # macOS
        font_paths = mac_fonts
    elif system == "Windows":
        font_paths = windows_fonts
    else:  # Linux
        # 优先使用动态查找的中文字体
        chinese_fonts_dynamic = find_chinese_fonts_linux()
        if chinese_fonts_dynamic:
            font_paths = chinese_fonts_dynamic + linux_fonts_static
        else:
            font_paths = linux_fonts_static
    
    # 尝试加载字体
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                # 如果是 .ttc 文件（TrueType Collection），需要指定索引
                if font_path.endswith('.ttc'):
                    return ImageFont.truetype(font_path, font_size, index=0)
                # .ttf 和 .otf 文件可以直接加载
                elif font_path.endswith(('.ttf', '.otf')):
                    return ImageFont.truetype(font_path, font_size)
                else:
                    # 其他格式也尝试加载
                    return ImageFont.truetype(font_path, font_size)
            except Exception as e:
                # 记录失败但不中断，继续尝试下一个字体
                print(f"Failed to load font {font_path}: {str(e)}")
                continue
    
    # 如果都失败，返回默认字体（不支持中文）
    print("Warning: No suitable font found, using default font (may not support Chinese)")
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
    width: Optional[int] = None  # 矩形宽度，用于文字填充
    height: Optional[int] = None  # 矩形高度，用于文字填充
    font_size: int = 24
    font_family: str = "arial.ttf"
    color: str = "#000000"
    align: str = "left"  # 对齐方式：left, center, right
    region: Optional[Region] = None  # 用于清除区域内的文字（inpainting）

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
        
        # 如果提供了宽度和高度，在矩形区域内填充文字
        if request.width and request.height and request.width > 0 and request.height > 0:
            # 计算文字在矩形内的位置
            text_x = request.x
            text_y = request.y
            
            # 根据对齐方式调整X坐标
            if request.align == "center":
                # 获取文字宽度（近似）
                bbox = draw.textbbox((0, 0), request.text, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = request.x + (request.width - text_width) // 2
            elif request.align == "right":
                bbox = draw.textbbox((0, 0), request.text, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = request.x + request.width - text_width
            
            # 如果文字宽度超过矩形宽度，需要换行
            bbox = draw.textbbox((0, 0), request.text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > request.width:
                # 需要换行处理
                # 对于中英文混合文本，按字符处理更准确
                lines = []
                current_line = ""
                
                # 将文本按空格分割成单词（英文）或字符（中文）
                import re
                # 使用正则表达式分割，保留空格
                tokens = re.findall(r'\S+|\s+', request.text)
                
                for token in tokens:
                    if token.isspace():
                        # 空格，尝试添加到当前行
                        test_line = current_line + token
                        test_bbox = draw.textbbox((0, 0), test_line, font=font)
                        test_width = test_bbox[2] - test_bbox[0]
                        
                        if test_width <= request.width:
                            current_line = test_line
                        else:
                            # 空格导致超宽，换行
                            if current_line:
                                lines.append(current_line.strip())
                            current_line = ""
                    else:
                        # 单词或字符
                        test_line = current_line + token
                        test_bbox = draw.textbbox((0, 0), test_line, font=font)
                        test_width = test_bbox[2] - test_bbox[0]
                        
                        if test_width <= request.width:
                            current_line = test_line
                        else:
                            # 超宽，需要换行
                            if current_line:
                                lines.append(current_line.strip())
                                current_line = token
                            else:
                                # 单个token就超过宽度，按字符拆分
                                for char in token:
                                    test_char_line = current_line + char
                                    test_char_bbox = draw.textbbox((0, 0), test_char_line, font=font)
                                    test_char_width = test_char_bbox[2] - test_char_bbox[0]
                                    
                                    if test_char_width <= request.width:
                                        current_line = test_char_line
                                    else:
                                        if current_line:
                                            lines.append(current_line.strip())
                                        current_line = char
                
                if current_line:
                    lines.append(current_line.strip())
                
                # 获取行高
                line_bbox = draw.textbbox((0, 0), "Ag", font=font)
                line_height = line_bbox[3] - line_bbox[1]
                
                # 绘制多行文字
                current_y = text_y
                for line in lines:
                    if current_y + line_height > request.y + request.height:
                        break  # 超出矩形高度，停止绘制
                    
                    # 根据对齐方式调整X坐标
                    line_x = text_x
                    if request.align == "center":
                        line_bbox = draw.textbbox((0, 0), line, font=font)
                        line_width = line_bbox[2] - line_bbox[0]
                        line_x = request.x + (request.width - line_width) // 2
                    elif request.align == "right":
                        line_bbox = draw.textbbox((0, 0), line, font=font)
                        line_width = line_bbox[2] - line_bbox[0]
                        line_x = request.x + request.width - line_width
                    
                    draw.text((line_x, current_y), line, fill=color, font=font)
                    current_y += line_height
            else:
                # 单行文字，直接绘制
                draw.text((text_x, text_y), request.text, fill=color, font=font)
        else:
            # 没有提供矩形尺寸，使用原来的方式
            draw.text((request.x, request.y), request.text, fill=color, font=font)
        
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

