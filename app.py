from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import base64
from PIL import Image
import io
from datetime import datetime

# 创建Flask应用实例
app = Flask(__name__, 
            template_folder='ai_generate/templates',
            static_folder='ai_generate/static')
CORS(app)  # 允许跨域请求

# 配置上传文件夹
UPLOAD_FOLDER = 'ai_generate/uploads'
GENERATED_FOLDER = 'ai_generate/generated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 上传图片接口
@app.route('/api/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # 保存上传的图片
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file.filename)[1]}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'filename': filename,
            'filepath': filepath
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 生图接口（临时实现）
@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # 临时实现：生成一个简单的占位图片
        # 在实际应用中，这里应该调用AI模型API
        img = Image.new('RGB', (512, 512), color=(73, 109, 137))
        
        # 保存生成的图片
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
        img.save(filepath)
        
        # 将图片转换为base64以便前端显示
        with open(filepath, "rb") as img_file:
            img_str = base64.b64encode(img_file.read()).decode('utf-8')
        
        return jsonify({
            'message': 'Image generated successfully',
            'filename': filename,
            'image_data': img_str
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 批量生成接口
@app.route('/api/batch-generate', methods=['POST'])
def batch_generate():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        count = data.get('count', 4)
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # 验证数量
        try:
            count = int(count)
            if count < 1 or count > 10:
                count = min(max(count, 1), 10)
        except ValueError:
            count = 4
        
        results = []
        for i in range(count):
            # 临时实现：为每个prompt生成一个占位图片
            variation = f" - 变化 {i+1}" if count > 1 else ""
            img = Image.new('RGB', (512, 512), color=(73 + i*20, 109 + i*10, 137 + i*15))
            
            # 保存生成的图片
            filename = f"batch_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.png"
            filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
            img.save(filepath)
            
            # 将图片转换为base64
            with open(filepath, "rb") as img_file:
                img_str = base64.b64encode(img_file.read()).decode('utf-8')
            
            results.append({
                'prompt': prompt + variation,
                'filename': filename,
                'image_data': img_str,
                'index': i
            })
        
        return jsonify({
            'message': 'Batch generation completed',
            'results': results,
            'images': results  # 同时返回两种格式以保持兼容性
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs('ai_generate/templates', exist_ok=True)
    os.makedirs('ai_generate/static', exist_ok=True)
    os.makedirs('ai_generate/static/css', exist_ok=True)
    os.makedirs('ai_generate/static/js', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)