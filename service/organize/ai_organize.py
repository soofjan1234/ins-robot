import os
from openai import OpenAI

def generate_ai_text(image_names):
    """
    使用AI生成文案内容
    
    Args:
        image_names: 图片名称列表
    
    Returns:
        dict: 包含生成的文案内容
    """
    
    # 初始化OpenAI客户端
    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=os.environ.get("ARK_API_KEY"),
    )
    
    # 构建提示词
    prompt = f"""
    请基于以下用户的5张图片名称，依次生成5个对应的英文翻译内容。
    
    图片名称:
    {', '.join(image_names)}
    
    返回格式为JSON，包含5个文案字段：text1, text2, text3, text4, text5
    """
    
    try:
        # 发送请求到AI模型
        completion = client.chat.completions.create(
            model="deepseek-v3-1-terminus",
            messages=[
                {"role": "system", "content": "你是一个专业的奢侈品英文翻译者。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # 获取AI回复内容
        ai_response = completion.choices[0].message.content
        
        print(f"AI生成成功: {ai_response}")
        
        # 清理AI回复，移除代码块标记
        cleaned_response = ai_response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:].strip()  # 移除 ```json
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3].strip()  # 移除 ```
        
        # 解析AI回复，提取文案内容
        texts = []
        
        # 尝试解析JSON格式的回复
        try:
            import json
            ai_data = json.loads(cleaned_response)
            # 如果AI返回的是JSON对象，提取text1到text5字段
            for i in range(1, 6):
                key = f"text{i}"
                if key in ai_data and ai_data[key].strip():
                    texts.append(ai_data[key].strip())
        except json.JSONDecodeError:
            # 如果不是JSON格式，按行分割处理
            lines = [line.strip() for line in cleaned_response.split('\n') if line.strip()]
            for line in lines:
                # 跳过JSON标记和空行
                if line in ['{', '}', '[', ']'] or line.startswith('"') and line.endswith('"'):
                    continue
                # 提取引号内的内容
                if '"' in line:
                    parts = line.split('"')
                    if len(parts) >= 4:  # key": "value"
                        value = parts[3]
                        if value.strip() and value != '':
                            texts.append(value.strip())
                elif line.strip() and not line.startswith('{'):
                    texts.append(line.strip())
        
        # 确保返回5个文案，不足则补充
        while len(texts) < 5:
            texts.append(f"AI生成的精彩文案{len(texts) + 1}")
        
        # 只取前5个
        texts = texts[:5]
        
        return {
            "success": True,
            "texts": texts[:5],
            "ai_response": ai_response
        }
        
    except Exception as e:
        print(f"AI生成失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "texts": ["AI生成失败，使用默认文案1", "AI生成失败，使用默认文案2", "AI生成失败，使用默认文案3", "AI生成失败，使用默认文案4", "AI生成失败，使用默认文案5"]
        }

if __name__ == "__main__":
    # 测试函数 - 使用data/photoshop文件夹中的实际图片
    test_image_names = [
        "19bag.jpg",
        "cf大mini.jpg", 
        "channel_2.55.jpg",
        "channel_woc.jpg",
        "荔枝纹牛皮mini黑金cf.jpg"
    ]
    
    result = generate_ai_text(test_image_names)
    print(f"测试结果: {result}")