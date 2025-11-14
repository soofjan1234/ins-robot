from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import base64
from PIL import Image
import io
from datetime import datetime

# 创建Flask应用实例
app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')
CORS(app)  # 允许跨域请求

# 配置上传文件夹
UPLOAD_FOLDER = 'ai_generate/uploads'
GENERATED_FOLDER = 'ai_generate/generated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

# 首页路由 - 导航页面
@app.route('/')
def index():
    return render_template('index.html')

# AI图片生成页面路由
@app.route('/ai_generate')
def ai_generate():
    return render_template('ai_generate.html')

# Instagram发布页面路由
@app.route('/instagram_publish')
def instagram_publish():
    return render_template('instagram_publish.html')

# 获取今日发布状态
@app.route('/api/publish/status', methods=['GET'])
def get_publish_status():
    try:
        from ins_robot.file_management_service import FileManagementService
        file_service = FileManagementService()
        
        # 获取今天的媒体文件
        media_files = file_service.get_media_files_for_today()
        
        # 获取当前日期信息
        from datetime import datetime
        today = datetime.now()
        weekday = today.weekday()
        
        # 检查是否在工作日
        is_workday = weekday < 5
        
        return jsonify({
            'has_images': len(media_files['images']) > 0,
            'has_texts': len(media_files['texts']) > 0,
            'image_count': len(media_files['images']),
            'text_count': len(media_files['texts']),
            'is_workday': is_workday,
            'today': today.strftime('%Y-%m-%d'),
            'weekday': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][weekday]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 执行发布操作
@app.route('/api/publish/execute', methods=['POST'])
def execute_publish():
    try:
        # 导入必要的模块
        from ins_robot.file_management_service import FileManagementService
        from ins_robot.media_upload_service import MediaUploadService
        from ins_robot.text_processing_service import TextProcessingService
        from ins_robot.login import InstagramLoginService
        from selenium import webdriver
        from datetime import datetime
        import time
        
        # 初始化服务
        file_service = FileManagementService()
        
        # 获取今天的媒体文件
        media_files = file_service.get_media_files_for_today()
        
        if not media_files['images']:
            return jsonify({'error': '未找到今日的图片文件'}), 400
        
        # 检查是否工作日
        weekday = datetime.now().weekday()
        if weekday >= 5:
            return jsonify({'error': '周末不支持发布'}), 400
        
        # 初始化浏览器
        from ins_robot.login import get_chrome_options, create_webdriver
        options = get_chrome_options(headless=True)  # 使用无头模式
        driver = create_webdriver(options)
        
        try:
            # 登录Instagram
            login_service = InstagramLoginService()
            login_success = login_service.login(driver)
            
            if not login_success:
                return jsonify({'error': 'Instagram登录失败'}), 400
            
            time.sleep(3)  # 等待页面加载
            
            # 初始化服务
            media_service = MediaUploadService(driver)
            text_service = TextProcessingService(driver)
            
            # 点击创建帖子按钮
            if not media_service.click_create_post_button():
                return jsonify({'error': '无法打开创建帖子界面'}), 400
            
            # 等待上传界面
            media_service.wait_for_upload_interface()
            
            # 上传第一张图片
            image_path = media_files['images'][0]
            if not media_service.upload_media(image_path):
                return jsonify({'error': '图片上传失败'}), 400
            
            # 点击下一步（两次）
            if not media_service.go_to_next_step() or not media_service.go_to_next_step():
                return jsonify({'error': '无法进入编辑界面'}), 400
            
            # 处理文案（如果有）
            if media_files['texts']:
                text_path = media_files['texts'][0]
                text_content = file_service.read_text_file(text_path)
                
                if text_content:
                    text_service.wait_for_textarea_ready()
                    processed_content = text_service.process_hashtags(text_content)
                    text_service.fill_caption_textarea(processed_content)
            
            # 发布帖子
            if not media_service.click_share_button():
                return jsonify({'error': '发布失败'}), 400
            
            return jsonify({
                'message': '发布成功！',
                'image_path': image_path,
                'has_text': len(media_files['texts']) > 0
            }), 200
            
        finally:
            driver.quit()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    os.makedirs('frontend/templates', exist_ok=True)
    os.makedirs('frontend/static', exist_ok=True)
    os.makedirs('frontend/static/css', exist_ok=True)
    os.makedirs('frontend/static/js', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)