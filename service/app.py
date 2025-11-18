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
        # 检查请求类型，支持 JSON 和 FormData
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            content = data.get('content', '')
            images = data.get('images', [])
            image_path = data.get('image_path', '')
        else:
            # 处理 FormData
            content = request.form.get('content', '')
            image_path = request.form.get('image_path', '')
            images = []
        
        print(f"发布请求 - 内容: {content[:50]}...")
        if image_path:
            print(f"图片路径: {image_path}")
        
        # 验证图片路径是否存在
        if image_path and not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'message': f'图片文件不存在: {image_path}'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '发布功能开发中...',
            'data': {
                'content_length': len(content),
                'image_path': image_path,
                'image_count': len(images),
                'status': 'processing'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发布失败: {str(e)}'
        }), 500

# /api/today-content 功能已删除 - 2025-11-18

@app.route('/api/weekday-images/<weekday>', methods=['GET'])
def get_weekday_images(weekday):
    try:
        # 验证星期参数
        valid_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if weekday not in valid_weekdays:
            return jsonify({
                'success': False,
                'message': f'无效的星期参数: {weekday}',
                'valid_weekdays': valid_weekdays
            }), 400
        
        # 构建媒体文件夹路径
        media_path = os.path.join('d:\otherWorkspace\ins-robot\data\media', weekday)
        
        if not os.path.exists(media_path):
            return jsonify({
                'success': False,
                'message': f'该星期文件夹不存在: {weekday}',
                'path': media_path
            })
        
        # 扫描文件夹中的图片文件
        files = os.listdir(media_path)
        images = []
        
        for file in files:
            file_path = os.path.join(media_path, file)
            if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                images.append({
                    'filename': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2)
                })
        
        return jsonify({
            'success': True,
            'message': f'成功获取{weekday}的图片列表',
            'data': {
                'weekday': weekday,
                'images': images,
                'total_images': len(images),
                'path': media_path
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取图片列表失败: {str(e)}'
        }), 500

@app.route('/api/text-content/<weekday>/<filename>', methods=['GET'])
def get_text_content(weekday, filename):
    try:
        # 验证星期参数
        valid_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if weekday not in valid_weekdays:
            return jsonify({
                'success': False,
                'message': f'无效的星期参数: {weekday}'
            }), 400
        
        # 验证文件名
        if not filename.lower().endswith('.txt'):
            return jsonify({
                'success': False,
                'message': '只支持txt文件'
            }), 400
        
        # 构建文本文件路径
        text_path = os.path.join('d:\otherWorkspace\ins-robot\data\media', weekday, filename)
        
        if not os.path.exists(text_path):
            return jsonify({
                'success': False,
                'message': f'文本文件不存在: {filename}'
            }), 404
        
        # 读取文本内容
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return jsonify({
                'success': True,
                'message': '成功获取文本内容',
                'data': {
                    'filename': filename,
                    'content': content,
                    'size': len(content),
                    'path': text_path
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'读取文本文件失败: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取文本内容失败: {str(e)}'
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
    print("  GET  /api/weekday-images/<weekday> - 获取指定星期图片列表")
    print("  GET  /api/text-content/<weekday>/<filename> - 获取文本内容")
    print("  GET  /health - 健康检查")
    print("\n服务启动在 http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)