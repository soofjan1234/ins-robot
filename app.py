from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
import base64
import json
import uuid
import threading
import queue
import time
import logging
from controller.clean import clean_files
from controller.load import load_to_generate_images

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

if __name__ == '__main__':
    print("Starting Instagram Robot Service...")
    print("\n服务启动在 http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)