from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
import logging
from controller.clean.clean import clean_files
from controller.load import load_to_generate_images, load_to_ps_imgs, load_to_refine_images, get_weekday_images, get_text_content
from controller.publish.publish import publish_post_api
from controller.generate.ai import regenerate_image, generate_ai_image
from controller.ps.ps import watermark_process_logic
from controller.organize.ai_text import generate_ai_text_api
from controller.organize.organize import organize_images_api

app = Flask(__name__)
CORS(app)

frontend_path = os.path.join((os.path.dirname(os.path.abspath(__file__))), 'frontend')

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

@app.route('/api/clean-files', methods=['POST'])
def clean_files_api():
    clean_files()
    return jsonify({"message": "Files cleaned successfully"}), 200


@app.route('/api/load-to-generate-imgs', methods=['GET'])
def load_to_generate_imgs_api():
    result = load_to_generate_images()
    if isinstance(result, tuple) and len(result) == 2:
        data, status_code = result
        return jsonify(data), status_code
    return jsonify(result), 200

@app.route('/api/load-to-ps-imgs', methods=['GET'])
def load_to_ps_imgs_api():
    result = load_to_ps_imgs()
    if isinstance(result, tuple) and len(result) == 2:
        data, status_code = result
        return jsonify(data), status_code
    return jsonify(result), 200

@app.route('/api/load-to-refine', methods=['GET'])
def load_to_refine_imgs_api():
    result = load_to_refine_images()
    if isinstance(result, tuple) and len(result) == 2:
        data, status_code = result
        return jsonify(data), status_code
    return jsonify(result), 200

# 图片重新生成接口
@app.route('/api/regenerate', methods=['POST'])
def regenerate():
    return regenerate_image()

# AI图片生成接口
@app.route('/api/ai-generate', methods=['POST'])
def generate_ai():
    return generate_ai_image()

@app.route('/api/watermark-process', methods=['POST'])
def watermark_process():
    return watermark_process_logic()

@app.route('/api/generate-ai-text', methods=['POST'])
def generate_ai_text():
    return generate_ai_text_api()

@app.route('/api/organize-images', methods=['POST'])
def organize_images():
    return organize_images_api()

@app.route('/api/weekday-images/<weekday>', methods=['GET'])
def weekday_images_api(weekday):
    result = get_weekday_images(weekday)
    if isinstance(result, tuple) and len(result) == 2:
        data, status_code = result
        return jsonify(data), status_code
    return jsonify(result), 200

@app.route('/api/text-content/<weekday>/<filename>', methods=['GET'])
def text_content_api(weekday, filename):
    result = get_text_content(weekday, filename)
    if isinstance(result, tuple) and len(result) == 2:
        data, status_code = result
        return jsonify(data), status_code
    return jsonify(result), 200

@app.route('/api/publish', methods=['POST'])
def publish_api():
    return publish_post_api()


if __name__ == '__main__':
    print("Starting Instagram Robot Service...")
    print("\n服务启动在 http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)