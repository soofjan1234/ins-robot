from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
import base64
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入水印处理模块
from ps.watermark import remove_watermark_inpaint, add_watermark
# 导入AI文案生成模块
from organize.ai_organize import generate_ai_text

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
            'today_content': '/api/today-content',
            'generate_ai_text': '/api/generate-ai-text'
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

@app.route('/api/watermark-process', methods=['POST'])
def watermark_process():
    """
    水印处理API - 循环调用remove_watermark_inpaint和add_watermark_to_image
    处理多张图片并保存结果到指定目录
    """
    try:
        data = request.get_json()
        images = data.get('images', [])  # Base64编码的图片数组或包含文件名信息的对象数组
        
        print(f"[水印处理API] 收到处理请求，图片数量: {len(images)}")
        
        if not images:
            return jsonify({
                'success': False,
                'message': '没有提供图片数据'
            }), 400
        
        # 创建结果保存目录
        result_dir = 'd:/otherWorkspace/ins-robot/data/ps_result'
        os.makedirs(result_dir, exist_ok=True)
        
        processed_images = []
        
        for i, image_item in enumerate(images):
            try:
                print(f"[水印处理API] 处理第 {i+1} 张图片...")
                
                # 处理新的数据结构：包含data和filename字段
                if isinstance(image_item, dict) and 'data' in image_item:
                    image_data = image_item['data']
                    original_filename = image_item.get('filename', f'image_{i}')
                else:
                    # 兼容旧的数据结构：直接是base64字符串
                    image_data = image_item
                    original_filename = f'image_{i}'
                
                # 从base64解码图片数据
                if ',' in image_data:
                    image_data = image_data.split(',')[1]  # 移除data:image/jpeg;base64,前缀
                
                image_bytes = base64.b64decode(image_data)
            
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_input = os.path.join(result_dir, f'temp_input_{timestamp}_{i}.jpg')
                temp_output = os.path.join(result_dir, f'temp_output_{timestamp}_{i}.jpg')
                final_output = os.path.join(result_dir, original_filename)
                
                # 保存原始图片到临时文件
                with open(temp_input, 'wb') as f:
                    f.write(image_bytes)
                
                print(f"[水印处理API] 第 {i+1} 步: 移除水印...")
                # 第一步：移除水印（使用内容感知填充）
                remove_watermark_inpaint(temp_input, temp_output)
                
                print(f"[水印处理API] 第 {i+1} 步: 添加新水印...")
                # 第二步：添加新水印
                add_watermark(temp_output, final_output)
                
                # 读取处理后的图片并转换为base64
                with open(final_output, 'rb') as f:
                    processed_image_bytes = f.read()
                
                processed_image_base64 = base64.b64encode(processed_image_bytes).decode('utf-8')
                
                processed_images.append({
                    'index': i,
                    'filename': original_filename,
                    'data': f'data:image/jpeg;base64,{processed_image_base64}',
                    'size': len(processed_image_bytes)
                })
                
                print(f"[水印处理API] 第 {i+1} 张图片处理完成")
                
                # 清理临时文件
                for temp_file in [temp_input, temp_output]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        
            except Exception as e:
                print(f"[水印处理API] 处理第 {i+1} 张图片失败: {str(e)}")
                # 继续处理下一张图片
                continue
        
        print(f"[水印处理API] 所有图片处理完成，成功处理: {len(processed_images)} 张")
        
        return jsonify({
            'success': True,
            'message': '水印处理完成',
            'data': {
                'total_processed': len(processed_images),
                'processed_images': processed_images,
                'result_directory': result_dir
            }
        })
        
    except Exception as e:
        print(f"[水印处理API] 处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'水印处理失败: {str(e)}'
        }), 500

def read_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

@app.route('/api/publish', methods=['POST'])
def publish_post():
    """
    Instagram发布API - 基于test_upload_post.py的实现
    执行完整的Instagram发布流程：登录、上传媒体、填充文案、发布
    """
    try:
        # 检查请求类型，支持 JSON 和 FormData
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            content = data.get('content', '')
            image_path = data.get('image_path', '')
            image_file = data.get('image_file', '')  # 图片文件名
            weekday = data.get('weekday', '')  # 星期几
        else:
            # 处理 FormData
            content = request.form.get('content', '')
            image_path = request.form.get('image_path', '')
            image_file = request.form.get('image_file', '')
            weekday = request.form.get('weekday', '')
        
        print(f"[发布API] 收到发布请求")
        print(f"[发布API] 内容长度: {len(content)}")
        print(f"[发布API] 图片路径: {image_path}")
        print(f"[发布API] 图片文件: {image_file}")
        print(f"[发布API] 星期: {weekday}")
        
        # 如果没有提供完整路径，尝试构建路径
        if not image_path and image_file and weekday:
            image_path = os.path.join('d:\\otherWorkspace\\ins-robot\\data\\media', weekday, image_file)
            print(f"[发布API] 构建图片路径: {image_path}")
        
        # 验证图片路径是否存在
        if image_path and not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'message': f'图片文件不存在: {image_path}'
            }), 400
        
        # 如果没有提供内容但提供了weekday和image_file，尝试读取对应的文本文件
        if not content and weekday and image_file:
            txt_filename = image_file.rsplit('.', 1)[0] + '.txt'
            txt_path = os.path.join('d:\\otherWorkspace\\ins-robot\\data\\media', weekday, txt_filename)
            print(f"[发布API] 尝试读取文本文件: {txt_path}")
            
            if os.path.exists(txt_path):
                content = read_file_content(txt_path)
                if content:
                    print(f"[发布API] 成功读取文本内容，长度: {len(content)}")
                else:
                    print(f"[发布API] 读取文本文件失败")
            else:
                print(f"[发布API] 文本文件不存在: {txt_path}")
        
        # 开始执行发布流程
        print("[发布API] 开始执行Instagram发布流程...")
        
        # 导入必要的模块
        try:
            from service.ins_robot.login import InstagramLoginService, get_chrome_options, create_webdriver
            from service.ins_robot.media_upload_service import MediaUploadService
            from service.ins_robot.text_processing_service import TextProcessingService
        except ImportError as e:
            print(f"[发布API] 导入模块失败: {e}")
            return jsonify({
                'success': False,
                'message': f'导入必要模块失败: {e}'
            }), 500
        
        driver = None
        try:
            # 1. 初始化浏览器
            print("[发布API] 正在初始化浏览器...")
            options = get_chrome_options(headless=False)
            driver = create_webdriver(options)
            
            # 2. 登录Instagram
            print("[发布API] 开始登录Instagram...")
            login_service = InstagramLoginService()
            login_success = login_service.login(driver)
            
            if not login_success:
                return jsonify({
                    'success': False,
                    'message': 'Instagram登录失败'
                }), 500
            
            # 等待页面完全加载
            print("[发布API] 登录成功，等待页面完全加载...")
            import time
            time.sleep(5)
            
            # 3. 初始化服务类
            media_service = MediaUploadService(driver)
            text_service = TextProcessingService(driver)
            
            # 4. 点击创建帖子按钮
            print("[发布API] 尝试点击创建帖子按钮...")
            create_success = media_service.click_create_post_button()
            
            if not create_success:
                return jsonify({
                    'success': False,
                    'message': '点击创建按钮失败'
                }), 500
            
            # 5. 等待上传界面加载
            print("[发布API] 创建按钮点击成功，等待上传界面...")
            upload_interface_ready = media_service.wait_for_upload_interface()
            
            if not upload_interface_ready:
                print("[发布API 警告] 上传界面检测失败，但将继续尝试上传")
            
            # 6. 上传图片文件
            print(f"[发布API] 尝试上传图片文件: {image_path}")
            upload_success = media_service.upload_media(image_path)
            
            if not upload_success:
                return jsonify({
                    'success': False,
                    'message': '文件上传失败'
                }), 500
            
            print("[发布API] 文件上传成功！")
            
            # 7. 点击下一步按钮
            print("[发布API] 点击下一步按钮...")
            media_service.go_to_next_step()
            
            # 8. 继续点击下一步按钮
            print("[发布API] 继续点击下一步按钮...")
            media_service.go_to_next_step()
            
            # 9. 处理文本内容
            if content:
                print("[发布API] 开始处理文本内容...")
                # 等待文本框准备就绪
                text_service.wait_for_textarea_ready()
                # 处理文本内容（包括标签）
                processed_content = text_service.process_hashtags(content)
                # 填充文本框
                text_service.fill_caption_textarea(processed_content)
                print("[发布API] 文本内容填充完成")
            else:
                print("[发布API] 没有文本内容需要填充")
            
            # 10. 点击分享按钮
            print("[发布API] 点击分享按钮...")
            media_service.click_share_button()
            
            print("[发布API] Instagram发布流程执行完成！")
            
            return jsonify({
                'success': True,
                'message': 'Instagram发布流程执行成功',
                'data': {
                    'content_length': len(content) if content else 0,
                    'image_path': image_path,
                    'status': 'completed',
                    'details': '完整的Instagram发布流程已执行完成，包括登录、上传、文案填充和发布'
                }
            })
            
        except Exception as e:
            print(f"[发布API] 执行发布流程时发生错误: {e}")
            return jsonify({
                'success': False,
                'message': f'执行发布流程失败: {str(e)}'
            }), 500
        finally:
            # 注意：这里不关闭浏览器，让用户可以观察结果
            if driver:
                print("[发布API] 发布流程结束，浏览器保持打开状态以便观察结果")
                # driver.quit()  # 暂时不关闭浏览器
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发布API处理失败: {str(e)}'
        }), 500

@app.route('/api/generate-ai-text', methods=['POST'])
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
        media_path = os.path.join('d:/otherWorkspace/ins-robot/data/media', weekday)
        
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
        text_path = os.path.join('d:/otherWorkspace/ins-robot/data/media', weekday, filename)
        
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

@app.route('/api/load-ps-images', methods=['GET'])
def load_ps_images():
    """
    加载PS结果文件夹中的图片
    返回图片列表和base64编码的图片数据
    """
    try:
        # PS结果文件夹路径
        ps_result_path = 'd:/otherWorkspace/ins-robot/data/ps_result'
        
        if not os.path.exists(ps_result_path):
            return jsonify({
                'success': False,
                'message': 'PS结果文件夹不存在',
                'path': ps_result_path
            }), 404
        
        # 扫描文件夹中的图片文件
        files = os.listdir(ps_result_path)
        images = []
        
        for file in files:
            file_path = os.path.join(ps_result_path, file)
            if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                try:
                    # 读取图片文件并转换为base64
                    with open(file_path, 'rb') as f:
                        image_bytes = f.read()
                    
                    # 转换为base64编码
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    images.append({
                        'filename': file,
                        'data': image_base64,
                        'size': len(image_bytes),
                        'size_mb': round(len(image_bytes) / (1024 * 1024), 2)
                    })
                    
                    print(f"[加载PS图片] 成功加载图片: {file} ({len(image_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"[加载PS图片] 处理图片 {file} 失败: {str(e)}")
                    continue
        
        print(f"[加载PS图片] 总共加载了 {len(images)} 张图片")
        
        return jsonify({
            'success': True,
            'message': f'成功加载 {len(images)} 张PS结果图片',
            'data': {
                'images': images,
                'total_images': len(images),
                'path': ps_result_path
            }
        })
        
    except Exception as e:
        print(f"[加载PS图片] 加载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'加载PS结果图片失败: {str(e)}'
        }), 500

@app.route('/api/organize-images', methods=['POST'])
def organize_images():
    """
    整理图片和文案到星期文件夹
    每个文件夹放一张图片和一个文案文件
    """
    try:
        data = request.get_json()
        
        # 获取参数
        image_names = data.get('image_names', [])  # 图片名称列表
        texts = data.get('texts', [])  # 文案列表
        
        if not image_names:
            return jsonify({
                'success': False,
                'message': '图片名称列表不能为空'
            }), 400
        
        if not texts:
            return jsonify({
                'success': False,
                'message': '文案列表不能为空'
            }), 400
        
        if len(image_names) != len(texts):
            return jsonify({
                'success': False,
                'message': f'图片数量({len(image_names)})与文案数量({len(texts)})不匹配'
            }), 400
        
        # 定义星期文件夹列表
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # 基础路径
        base_media_path = 'd:/otherWorkspace/ins-robot/data/media'
        ps_result_path = 'd:/otherWorkspace/ins-robot/data/ps_result'
        
        # 确保media基础路径存在
        os.makedirs(base_media_path, exist_ok=True)
        
        # 先清空每个星期文件夹下的文件
        print("[整理] 开始清空星期文件夹...")
        for weekday in weekdays:
            weekday_path = os.path.join(base_media_path, weekday)
            if not os.path.exists(weekday_path):
                # 如果文件夹不存在，创建它
                os.makedirs(weekday_path, exist_ok=True)
                print(f"[整理] 创建文件夹: {weekday_path}")
        
        print("[整理] 星期文件夹清空完成")
        
        organized_files = []
        
        # 遍历图片和文案
        for i, (image_name, text) in enumerate(zip(image_names, texts)):
            # 如果图片数量超过7个，循环使用星期文件夹
            weekday = weekdays[i % len(weekdays)]
            
            # 创建星期文件夹
            weekday_path = os.path.join(base_media_path, weekday)
            os.makedirs(weekday_path, exist_ok=True)
            
            # 源图片路径
            source_image_path = os.path.join(ps_result_path, image_name)
            
            if not os.path.exists(source_image_path):
                print(f"[整理] 图片不存在: {source_image_path}")
                continue
            
            # 目标图片路径
            target_image_path = os.path.join(weekday_path, image_name)
            
            try:
                # 复制图片到目标文件夹
                import shutil
                shutil.copy2(source_image_path, target_image_path)
                print(f"[整理] 复制图片: {image_name} -> {weekday_path}")
                
                # 创建对应的文案文件
                text_filename = f"{os.path.splitext(image_name)[0]}.txt"
                text_file_path = os.path.join(weekday_path, text_filename)
                
                # 写入文案内容
                with open(text_file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                print(f"[整理] 创建文案: {text_filename} -> {weekday_path}")
                
                organized_files.append({
                    'weekday': weekday,
                    'image_name': image_name,
                    'text_filename': text_filename,
                    'image_path': target_image_path,
                    'text_path': text_file_path
                })
                
            except Exception as e:
                print(f"[整理] 处理文件 {image_name} 失败: {str(e)}")
                continue
        
        if not organized_files:
            return jsonify({
                'success': False,
                'message': '没有成功整理任何文件'
            }), 400
        
        return jsonify({
            'success': True,
            'message': f'成功整理了 {len(organized_files)} 个文件',
            'data': {
                'total_organized': len(organized_files),
                'organized_files': organized_files,
                'weekdays_used': list(set(f['weekday'] for f in organized_files))
            }
        })
        
    except Exception as e:
        print(f"[整理] API处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'整理文件失败: {str(e)}'
        }), 500

@app.route('/api/clean-files', methods=['POST'])
def clean_files():
    """
    清理功能API - 清理三个文件夹中的图片和txt文件
    """
    try:
        # 定义要清理的三个文件夹路径
        base_dir = 'd:/otherWorkspace/ins-robot/data'
        clean_paths = [
            os.path.join(base_dir, 'ps_result'),
            os.path.join(base_dir, 'photoshop'),
            os.path.join(base_dir, 'media')
        ]
        
        print(f"[清理功能] 开始清理三个文件夹")
        
        # 统计信息
        total_image_count = 0
        total_txt_count = 0
        total_file_count = 0
        total_size = 0
        
        # 清理结果
        results = []
        
        # 遍历每个要清理的路径
        for clean_path in clean_paths:
            print(f"[清理功能] 开始清理路径: {clean_path}")
            
            # 检查路径是否存在
            if not os.path.exists(clean_path):
                print(f"[清理功能] 路径不存在: {clean_path}")
                results.append({
                    'path': clean_path,
                    'status': 'skipped',
                    'reason': '路径不存在'
                })
                continue
            
            # 本路径的统计信息
            path_image_count = 0
            path_txt_count = 0
            path_file_count = 0
            path_size = 0
            
            # 递归遍历文件夹
            for root, dirs, files in os.walk(clean_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 只清理图片文件和txt文件
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) or \
                       file.lower().endswith('.txt'):
                        try:
                            file_size = os.path.getsize(file_path)
                            path_size += file_size
                            
                            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                                path_image_count += 1
                            elif file.lower().endswith('.txt'):
                                path_txt_count += 1
                            
                            os.remove(file_path)
                            path_file_count += 1
                            print(f"[清理功能] 已删除: {file_path}")
                            
                        except Exception as e:
                            print(f"[清理功能] 删除文件失败 {file_path}: {str(e)}")
                            # 继续清理其他文件
                            continue
            
            # 更新总数统计
            total_image_count += path_image_count
            total_txt_count += path_txt_count
            total_file_count += path_file_count
            total_size += path_size
            
            # 添加本路径的结果
            results.append({
                'path': clean_path,
                'status': 'completed',
                'image_files_cleaned': path_image_count,
                'text_files_cleaned': path_txt_count,
                'total_files_cleaned': path_file_count,
                'size_cleaned_mb': round(path_size / (1024 * 1024), 2)
            })
        
        # 转换总大小为MB
        total_size_mb = round(total_size / (1024 * 1024), 2)
        
        print(f"[清理功能] 全部清理完成 - 图片: {total_image_count}, 文本: {total_txt_count}, 总文件数: {total_file_count}, 总大小: {total_size_mb}MB")
        
        return jsonify({
            'success': True,
            'message': '三个文件夹清理完成',
            'data': {
                'total_image_files_cleaned': total_image_count,
                'total_text_files_cleaned': total_txt_count,
                'total_files_cleaned': total_file_count,
                'total_size_cleaned_mb': total_size_mb,
                'folder_results': results
            }
        })
        
    except Exception as e:
        print(f"[清理功能] 清理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文件清理失败: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Instagram Robot Service'
    })

if __name__ == '__main__':
    print("Starting Instagram Robot Service...")
    print("\n服务启动在 http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)