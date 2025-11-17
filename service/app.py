from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

# 配置静态文件路径
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

# 主页路由
@app.route('/')
def index():
    return send_from_directory(os.path.join(frontend_path, 'html'), 'index.html')

# 静态文件路由 - 统一处理所有静态资源
@app.route('/<path:filename>')
def serve_static(filename):
    if filename.startswith('css/') or filename.startswith('js/'):
        return send_from_directory(frontend_path, filename)
    return send_from_directory(os.path.join(frontend_path, 'html'), filename)

# API状态接口
@app.route('/api/status')
def api_status():
    return jsonify({
        'message': 'Instagram Robot Service is running!',
        'version': '1.0.0',
        'endpoints': {
            'generate': '/api/generate',
            'edit': '/api/edit', 
            'publish': '/api/publish',
            'today_content': '/api/today-content'
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

@app.route('/api/today-content', methods=['GET'])
def get_today_content():
    try:
        # 获取今天是星期几（0=Monday, 6=Sunday）
        today = datetime.now().weekday()
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        today_folder = weekdays[today]
        
        # 构建媒体文件夹路径
        media_path = os.path.join('d:\\otherWorkspace\\ins-robot\\data\\media', today_folder)
        
        if not os.path.exists(media_path):
            return jsonify({
                'success': False,
                'message': f'今日内容文件夹不存在: {today_folder}',
                'data': {
                    'today': today_folder,
                    'path': media_path
                }
            })
        
        # 扫描文件夹中的文件
        files = os.listdir(media_path)
        images = []
        texts = []
        
        for file in files:
            file_path = os.path.join(media_path, file)
            if os.path.isfile(file_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    images.append({
                        'filename': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
                elif file.lower().endswith('.txt'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                texts.append({
                                    'filename': file,
                                    'content': content,
                                    'size': len(content)
                                })
                    except Exception as e:
                        print(f"读取文本文件失败 {file}: {e}")
        
        return jsonify({
            'success': True,
            'message': '成功获取今日内容',
            'data': {
                'today': today_folder,
                'images': images,
                'texts': texts,
                'total_files': len(images) + len(texts)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取今日内容失败: {str(e)}'
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
    print("  GET  / - 主页")
    print("  GET  /api/status - API状态")
    print("  POST /api/generate - 生图功能")
    print("  POST /api/edit - P图功能") 
    print("  POST /api/publish - 发布功能")
    print("  GET  /api/today-content - 获取今日内容")
    print("  GET  /health - 健康检查")
    print("\n服务启动在 http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)