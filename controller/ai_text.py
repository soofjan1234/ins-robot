from flask import request, jsonify
from service.organize.ai_organize import generate_ai_text

def generate_ai_text_api():
    """
    AI文案生成API - 基于用户输入的文案和图片名称生成优化后的文案内容
    """
    try:
        data = request.get_json()
        image_names = data.get('image_names', [])  # 图片名称列表
        
        print(f"[AI文案生成API] 收到生成请求")
        print(f"[AI文案生成API] 图片名称数量: {len(image_names)}")
        print(f"[AI文案生成API] 图片名称: {image_names}")
        
        # 验证输入数据
        if not image_names:
            return jsonify({
                'success': False,
                'message': '请提供图片名称'
            }), 400
        
        # 调用AI文案生成函数
        result = generate_ai_text(image_names)
        
        if result['success']:
            print(f"[AI文案生成API] AI文案生成成功")
            return jsonify({
                'success': True,
                'message': 'AI文案生成成功',
                'texts': result['texts'],  # 直接返回texts字段
                'total_generated': len(result['texts']),
                'ai_response': result.get('ai_response', ''),
                'model': 'deepseek-v3-1-terminus'
            })
        else:
            print(f"[AI文案生成API] AI文案生成失败: {result.get('error', '未知错误')}")
            return jsonify({
                'success': False,
                'message': f'AI文案生成失败: {result.get("error", "未知错误")}',
                'texts': result['texts'],  # 返回默认文案
                'error': result.get('error', '未知错误')
            }), 500
            
    except Exception as e:
        print(f"[AI文案生成API] 处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'AI文案生成API处理失败: {str(e)}'
        }), 500