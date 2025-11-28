import requests
import json
import re
import base64
import os
import mimetypes
from datetime import datetime

def load_local_image(image_path):
    """读取本地图片文件并转换为base64格式"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 转换为base64
        img_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 获取图片MIME类型
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = 'image/png'  # 默认为PNG
        
        return img_base64, mime_type
    except Exception as e:
        print(f"读取图片 {image_path} 失败: {e}")
        return None, None

def save_base64_image(base64_data, filename=None):
    """保存base64图片数据到文件"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}.png"
    
    try:
        # 解码base64数据
        image_data = base64.b64decode(base64_data)
        
        # 保存到文件
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        print(f"\n📸 图片已保存: {filename}")
        print(f"📂 完整路径: {os.path.abspath(filename)}")
        
        return filename
    except Exception as e:
        print(f"\n❌ 保存图片失败: {e}")
        return None

def extract_base64_from_markdown(text):
    """从markdown格式中提取base64图片数据"""
    # 匹配 ![image](data:image/png;base64,...) 格式
    pattern = r'!\[image\]\(data:image/[^;]+;base64,([A-Za-z0-9+/=]+)\)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def chat(image_file):
    img_base64, mime_type = load_local_image(image_file)
    if img_base64:
        return {
            'text_content': '这是模拟的AI生成文本。',
            'image_base64': img_base64,
            'filename': os.path.basename(image_file)
        }
    return {'error': '无法加载图片进行模拟返回。'}


    api_url = "https://new.12ai.org"
    # 替换为你的密钥
    api_key = "sk-gUgJOMDAibsKjhzYwdqvA2tDWIuLK5FlfRU1Nx3CBxgXn1R9"
    model = "gemini-2.5-flash-image"
    
    # 英文提示词(必需为英文)
    user_question = """Create a high-end luxury bag showcase image by placing the bag from the first image onto the table in the second image, 
    using the second image as the background. 
    The bag should look naturally positioned on the table, with an effect similar to the third image. 
    Keep the angles of both the bag and the background table unchanged"""
    
    # 图片列表
    images = [image_file, os.path.join(os.path.dirname(__file__), "2.jpg"), os.path.join(os.path.dirname(__file__), "3.jpg")]
    
    # 构建请求内容
    parts = [{"text": user_question}]
    for image_path in images:
        img_base64, mime_type = load_local_image(image_path)
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": img_base64
            }
        })
    
    data = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096,
            "topP": 1.0
        },
        "stream": False
    }

    try:
        response = requests.post(
            f"{api_url}/v1beta/models/{model}:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30,
            verify=False
        )
        
        if response.status_code != 200:
            print(f"错误: {response.status_code}")
            print(response.text[:1000])  # 截断错误信息
            return

        result = response.json()
        # 简化响应处理
        for candidate in result.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'text' in part:
                    text_content = part['text']
                    print(text_content[:1000])  # 截断原始输出
                    
                    # 检查并保存图片
                    base64_data = extract_base64_from_markdown(text_content)
                    if base64_data:
                        saved_filename = save_base64_image(base64_data, filename=f"ai_generated_{os.path.basename(image_file)}")
                        return {
                            'text_content': text_content,
                            'image_base64': base64_data,
                            'filename': saved_filename
                        }
        return None # 如果没有生成图片，返回 None
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return {'error': f"请求错误: {e}"}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return {'error': f"JSON解析错误: {e}"}

if __name__ == "__main__":
    # 提供一个默认的图片文件路径，或者从命令行参数获取
    default_image_file = os.path.join(os.path.dirname(__file__), "1.jpg") # 假设 1.jpg 在 ai.py 同级目录
    chat(default_image_file)