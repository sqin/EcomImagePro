# -*- coding: utf-8 -*-
import os
import json
import io
import uuid
from PIL import Image
from dotenv import load_dotenv

from alibabacloud_ocr_api20210707.client import Client as ocr_api20210707Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_credentials.models import Config as CredentialConfig

load_dotenv()


def create_client() -> ocr_api20210707Client:
    """
    使用凭据初始化账号Client
    @return: Client
    @throws Exception
    """
    credentialsConfig = CredentialConfig(
        type='access_key',
        access_key_id=os.environ.get('ALIYUN_ACCESS_KEY_ID'),
        access_key_secret=os.environ.get('ALIYUN_ACCESS_KEY_SECRET')
    )
    credentialsClient = CredentialClient(credentialsConfig)
    config = open_api_models.Config(
        credential=credentialsClient
    )
    # Endpoint 请参考 https://api.aliyun.com/product/ocr-api
    config.endpoint = f'ocr-api.cn-hangzhou.aliyuncs.com'
    return ocr_api20210707Client(config)


def extract_text_from_region(image_roi, original_image_path, region):
    """
    使用阿里云OCR服务从图片区域中提取文字
    
    Args:
        image_roi: PIL Image对象（选中区域的图片）
        original_image_path: 原始图片路径
        region: 区域信息字典，包含x, y, width, height
    
    Returns:
        识别出的文字字符串和临时图片路径的元组 (text, temp_image_path)
    """
    temp_image_path = None
    try:
        # 检查环境变量
        if not os.environ.get('ALIYUN_ACCESS_KEY_ID') or not os.environ.get('ALIYUN_ACCESS_KEY_SECRET'):
            raise ValueError("ALIYUN_ACCESS_KEY_ID和ALIYUN_ACCESS_KEY_SECRET未配置，请在.env文件中设置")
        
        # 创建临时目录
        temp_dir = "temp_ocr"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 保存裁剪的图片到临时目录
        temp_filename = f"ocr_region_{uuid.uuid4().hex}.png"
        temp_image_path = os.path.join(temp_dir, temp_filename)
        
        # 如果图片是RGBA模式，转换为RGB
        if image_roi.mode == 'RGBA':
            rgb_image = Image.new('RGB', image_roi.size, (255, 255, 255))
            rgb_image.paste(image_roi, mask=image_roi.split()[3])
            image_roi = rgb_image
        
        # 保存图片到临时目录
        image_roi.save(temp_image_path, format='PNG')
        print(f"OCR区域图片已保存到: {temp_image_path}")
        
        # 将PIL Image转换为字节流用于OCR API
        buffer = io.BytesIO()
        image_roi.save(buffer, format='PNG')
        buffer.seek(0)  # 重置指针到开始位置
        
        # 创建客户端
        client = create_client()
        runtime = util_models.RuntimeOptions()
        
        # 调用阿里云OCR API - 使用RecognizeBasic接口
        recognize_basic_request = ocr_api_20210707_models.RecognizeBasicRequest(
            body=buffer
        )
        resp = client.recognize_basic_with_options(recognize_basic_request, runtime)
        
        # 检查响应状态
        if resp.status_code != 200:
            print(f"OCR API返回错误状态码: {resp.status_code}")
            if resp.body and resp.body.message:
                print(f"错误信息: {resp.body.message}")
            return "", temp_image_path
        
        # 解析响应结果
        # resp.body.data 是一个JSON字符串，需要解析
        if not resp.body or not resp.body.data:
            print("OCR API返回数据为空")
            return "", temp_image_path
        
        try:
            data_json = json.loads(resp.body.data)
            # 提取文字内容，根据API文档，可能的结构是 content 或 results
            content = ""
            if isinstance(data_json, dict):
                # 尝试不同的字段名
                content = data_json.get('content', '') or data_json.get('text', '')
                # 如果有results数组，提取所有文字
                if not content and 'results' in data_json:
                    results = data_json.get('results', [])
                    if isinstance(results, list):
                        text_parts = []
                        for item in results:
                            if isinstance(item, dict):
                                text_parts.append(item.get('text', '') or item.get('content', ''))
                            elif isinstance(item, str):
                                text_parts.append(item)
                        content = ' '.join(text_parts)
            elif isinstance(data_json, str):
                content = data_json
            
            # 清理文本
            text = content.strip() if content else ""
            return text, temp_image_path
        except json.JSONDecodeError as e:
            print(f"解析OCR响应JSON失败: {str(e)}")
            print(f"原始数据: {resp.body.data}")
            return "", temp_image_path
        
    except Exception as e:
        print(f"OCR识别错误: {str(e)}")
        # 如果错误有message属性，打印出来
        if hasattr(e, 'message'):
            print(f"错误信息: {e.message}")
        # 如果错误有data属性，打印诊断地址
        if hasattr(e, 'data') and e.data:
            print(f"诊断地址: {e.data.get('Recommend', '')}")
        return "", temp_image_path
