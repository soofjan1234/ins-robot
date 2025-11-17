from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'Instagram Robot Service is running!',
        'version': '1.0.0',
        'endpoints': {
            'generate': '/api/generate',
            'edit': '/api/edit', 
            'publish': '/api/publish'
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        print(f"生图请求 - 提示词: {prompt}")
        
        return jsonify({
            'success': True,
            'message': '生图功能开发中...',
            'data': {
                'prompt': prompt,
                'status': 'processing'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生图失败: {str(e)}'
        }), 500

@app.route('/api/edit', methods=['POST'])
def edit_image():
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        edit_type = data.get('edit_type', '')
        
        print(f"P图请求 - 编辑类型: {edit_type}")
        
        return jsonify({
            'success': True,
            'message': 'P图功能开发中...',
            'data': {
                'edit_type': edit_type,
                'status': 'processing'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'P图失败: {str(e)}'
        }), 500

@app.route('/api/publish', methods=['POST'])
def publish_post():
    try:
        data = request.get_json()
        content = data.get('content', '')
        images = data.get('images', [])
        
        print(f"发布请求 - 内容: {content[:50]}...")
        
        return jsonify({
            'success': True,
            'message': '发布功能开发中...',
            'data': {
                'content_length': len(content),
                'image_count': len(images),
                'status': 'processing'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发布失败: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Instagram Robot Service'
    })

if __name__ == '__main__':
    print("Starting Instagram Robot Service...")
    print("Available endpoints:")
    print("  GET  / - 服务状态")
    print("  POST /api/generate - 生图功能")
    print("  POST /api/edit - P图功能") 
    print("  POST /api/publish - 发布功能")
    print("  GET  /health - 健康检查")
    print("\n服务启动在 http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)