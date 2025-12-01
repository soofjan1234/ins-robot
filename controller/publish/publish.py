import os
import time
from flask import request, jsonify

def read_file_content(file_path):
    """
    读取文件内容
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        str: 文件内容，如果读取失败返回空字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[读取文件] 失败: {str(e)}")
        return ''

def publish_post_api():
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
        
        # 如果没有提供完整路径，尝试构建路径 - 使用toPublish目录而不是media目录
        if not image_path and image_file and weekday:
            image_path = os.path.join('d:\\otherWorkspace\\ins-robot\\data\\toPublish', weekday, image_file)
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
            txt_path = os.path.join('d:\\otherWorkspace\\ins-robot\\data\\toPublish', weekday, txt_filename)
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