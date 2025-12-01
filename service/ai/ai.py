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
        print(f"匹配到的base64数据: {match.group(1)[:50]}...")  # 截断输出
        return match.group(1)
    print("未匹配到base64图片数据")
    return None

def chat(image_file):
    # 英文提示词(必需为英文)
    user_question = """Create a high-end luxury bag showcase image by placing the bag from the first image onto the table in the second image, 
    using the second image as the background. 
    The bag should look naturally positioned on the table, with an effect similar to the third image. 
    Keep the angles of both the bag and the background table unchanged"""
    
    # 配置API参数
    api_key = "sk-gUgJOMDAibsKjhzYwdqvA2tDWIuLK5FlfRU1Nx3CBxgXn1R9"
    model = "gemini-2.5-flash-image"
    api_url = f"https://cdn.12ai.org/v1beta/models/{model}:generateContent?key={api_key}"
    
    # 加载主图片（用户上传的图片）
    img_base64, mime_type = load_local_image(image_file)
    if not img_base64:
        print("无法加载图片")
        return {'error': '无法加载图片'}
    
    # 添加所有需要的图片
    images = [image_file, os.path.join(os.path.dirname(__file__), "2.jpg"), os.path.join(os.path.dirname(__file__), "3.jpg")]
    
    # 构建请求内容（按照新API格式）
    parts = [{"text": user_question}]
    
    # 添加所有图片到parts数组
    for img_path in images:
        img_base64, img_mime = load_local_image(img_path)
        if img_base64:
            parts.append({
                "inline_data": {
                    "mime_type": img_mime,
                    "data": img_base64
                }
            })
            print(f"已添加图片: {os.path.basename(img_path)}")
    
    data = {
        "contents": [{
            "parts": parts
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "1:1"
            }
        }
    }

    try:
        print(f"发送请求到: {api_url}")
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=60,  # 增加超时时间
            verify=False
        )
        
        if response.status_code != 200:
            print(f"API错误: 状态码 {response.status_code}")
            print(f"错误信息: {response.text}")
            return {'error': f'API返回错误: {response.status_code}, {response.text[:200]}'}

        result = response.json()
        print("API响应成功，开始解析")
        
        
        # 按照新的响应格式处理结果
        # 从candidates[0].content.parts中查找inline_data
        text_content = ""
        base64_data = None
        
        for candidate in result.get('candidates', []):
            content = candidate.get('content', {})
            for part in content.get('parts', []):
                # 获取文本内容
                if 'text' in part:
                    text_content = part['text']
                    print(f"原始文本内容: {text_content[:200]}...")
                
                # 直接从inline_data获取图片数据（新格式）
                if 'inlineData' in part:
                    inline_data = part['inlineData']
                    if 'data' in inline_data:
                        base64_data = inline_data['data']
                        print(f"找到内联图片数据，长度: {len(base64_data)} 字符")
                        break
            if base64_data:
                break
        
        if base64_data:
            # 保存生成的图片
            saved_filename = save_base64_image(base64_data, filename=f"ai_generated_{os.path.basename(image_file)}")
            print(f"图片保存成功: {saved_filename}")
            return {
                'success': True,
                'text_content': text_content,
                'image_base64': base64_data,
                'filename': saved_filename
            }
        else:
            print("未在响应中找到内联图片数据")
            return {'error': '未在API响应中找到生成的图片数据'}
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {str(e)}")
        return {'error': f"请求错误: {str(e)}"}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        print(f"原始响应: {response.text[:200]}...")
        return {'error': f"JSON解析错误: {str(e)}"}
    except Exception as e:
        print(f"处理异常: {str(e)}")
        return {'error': f"处理错误: {str(e)}"}

if __name__ == "__main__":
    # 提供一个默认的图片文件路径，或者从命令行参数获取
    default_image_file = os.path.join(os.path.dirname(__file__), "1.jpg") # 假设 1.jpg 在 ai.py 同级目录
    chat(default_image_file)