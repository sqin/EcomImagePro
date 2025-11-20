import os
from dotenv import load_dotenv
import dashscope
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role

load_dotenv()

# 初始化通义千问API
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY", "")

# 语言代码映射
LANG_MAP = {
    'zh': '中文',
    'en': 'English',
    'ru': 'Russian'
}

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    使用通义千问API进行翻译
    
    Args:
        text: 要翻译的文本
        source_lang: 源语言代码 ('zh', 'en', 'ru')
        target_lang: 目标语言代码 ('zh', 'en', 'ru')
    
    Returns:
        翻译后的文本
    """
    if not dashscope.api_key:
        raise ValueError("DASHSCOPE_API_KEY未配置，请在.env文件中设置")
    
    source_name = LANG_MAP.get(source_lang, source_lang)
    target_name = LANG_MAP.get(target_lang, target_lang)
    
    prompt = f"请将以下{source_name}文本翻译成{target_name}，只返回翻译结果，不要添加任何解释：\n{text}"
    
    try:
        # 使用messages格式调用API
        messages = [
            {'role': Role.USER, 'content': prompt}
        ]
        
        response = Generation.call(
            model='qwen-mt-plus',
            messages=messages,
            max_tokens=1000
        )
        
        if response.status_code == 200:
            # 根据响应格式提取文本
            if hasattr(response, 'output'):
                if hasattr(response.output, 'choices') and response.output.choices:
                    # messages格式返回
                    translated_text = response.output.choices[0].message.content.strip()
                elif hasattr(response.output, 'text'):
                    # prompt格式返回
                    translated_text = response.output.text.strip()
                else:
                    raise Exception("无法从响应中提取翻译结果")
            else:
                raise Exception("响应格式不正确")
            
            return translated_text
        else:
            raise Exception(f"翻译API调用失败: {response.message}")
    except Exception as e:
        raise Exception(f"翻译失败: {str(e)}")

