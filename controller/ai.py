import os
import sys
import time
import uuid
import threading
import queue
import base64
from datetime import datetime
from flask import request, jsonify

# 添加service目录到路径，以便导入ai模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 全局图片处理队列
image_processing_queue = queue.Queue()
# 结果存储字典
processing_results = {}
# 结果锁，确保线程安全
results_lock = threading.Lock()
# 任务完成事件字典
task_events = {}
# tmpPath与resultPath的映射字典，用于重新生成功能
tmp_result_map = {}
# 映射字典锁，确保线程安全
tmp_result_map_lock = threading.Lock()

# 工作协程函数 - 处理队列中的图片
def image_processor_worker():
    """
    图片处理工作协程，从队列中获取图片任务并处理
    """
    print("[图片处理协程] 启动图片处理工作协程")
    while True:
        try:
            # 从队列中获取任务
            task = image_processing_queue.get()
            if task is None:  # 退出信号
                print("[图片处理协程] 接收到退出信号，协程终止")
                image_processing_queue.task_done()
                break
            
            task_id = task['task_id']
            original_filename = task['original_filename']
            
            # 检查任务类型，处理不同的数据结构
            is_regenerate = task.get('is_regenerate', False)
            
            if is_regenerate:
                # 重新生成任务，直接使用image_data和filename
                image_data = task['image_data']
                filename = task['filename']
                # 对于重新生成任务，temp_filepath需要重新构建为绝对路径
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                temp_dir = os.path.join(base_dir, 'data', 'temp_ai_images')
                temp_filepath = os.path.join(temp_dir, filename)

                print(f"[图片处理协程] 开始处理重新生成任务 {task_id}, 文件: {original_filename}")
            else:
                # 普通生成任务，使用temp_filepath
                temp_filepath = task['temp_filepath']
                print(f"[图片处理协程] 开始处理任务 {task_id}, 文件: {original_filename}")
            
            try:
                # 导入chat函数
                from service.ai.ai import chat
                
                # 调用AI处理函数
                ai_result = chat(temp_filepath)
                # 先检查ai_result是否为None，避免'NoneType' object is not iterable错误
                if ai_result is None or not isinstance(ai_result, dict):
                    result = {
                        'success': False,
                        'message': 'AI处理失败: 返回结果格式错误',
                        'filename': original_filename
                    }
                elif 'error' in ai_result:
                    result = {
                        'success': False,
                        'message': f'AI处理失败: {ai_result["error"]}',
                        'filename': original_filename
                    }
                else:
                    # 提取处理后的结果
                    text_content = ai_result.get('text_content', '')
                    image_base64 = ai_result.get('image_base64', '')
                    
                    if not image_base64:
                        result = {
                            'success': False,
                            'message': 'AI处理未返回图片数据',
                            'filename': original_filename
                        }
                    else:
                        # 构建成功结果
                        image_url = f'data:image/jpeg;base64,{image_base64}'
                        
                
                        result = {
                            'success': True,
                            'message': 'AI图片生成成功',
                            'data': {
                                'text_content': text_content,
                                'image': image_url,
                                'filename': tops_filename
                            }
                        }
                        
                        # 建立tmpPath和resultPath的映射关系
                        with tmp_result_map_lock:
                            tmp_result_map[image_url] = temp_filepath
                
                # 保存结果到字典（线程安全）
                with results_lock:
                    if task_id not in processing_results:
                        processing_results[task_id] = []
                    processing_results[task_id].append(result)
                
                print(f"[图片处理协程] 任务 {task_id}, 文件: {original_filename} 处理完成")
                
            except Exception as e:
                error_msg = f"处理图片时出错: {str(e)}"
                print(f"[图片处理协程] {error_msg}")
                
                # 保存错误结果（线程安全）
                with results_lock:
                    if task_id not in processing_results:
                        processing_results[task_id] = []
                    processing_results[task_id].append({
                        'success': False,
                        'message': error_msg,
                        'filename': original_filename
                    })
            finally:
                # 标记任务完成
                image_processing_queue.task_done()
                # 减少待处理计数并通知
                with results_lock:
                    if task_id in task_events and len(processing_results.get(task_id, [])) == task_events[task_id]['total']:
                        task_events[task_id]['event'].set()  # 触发完成事件
            
        except Exception as e:
            print(f"[图片处理协程] 协程内部错误: {str(e)}")
            try:
                # 确保队列任务标记为完成
                image_processing_queue.task_done()
            except:
                pass

# 启动工作协程
processor_thread = threading.Thread(target=image_processor_worker, daemon=True)
processor_thread.start()

def regenerate_image():
    """图片重新生成接口"""
    try:
        # 获取请求数据
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': '缺少必要的图片参数'}), 400
            
        image_url = data['image']
        index = data.get('index', 0)
        
        # 从映射字典中查找对应的tmpPath
        with tmp_result_map_lock:
            if image_url not in tmp_result_map:
                return jsonify({'success': False, 'message': '未找到对应的原始图片文件'}), 404
            temp_image_path = tmp_result_map[image_url]
        
        # 检查文件是否存在
        if not os.path.exists(temp_image_path):
            return jsonify({'success': False, 'message': '图片文件不存在'}), 404
            
        # 读取图片文件内容
        with open(temp_image_path, 'rb') as f:
            image_data = f.read()
        
        # 从临时文件路径获取文件名
        filename = os.path.basename(temp_image_path)
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务数据，与现有队列处理格式保持一致
        task_data = {
            'task_id': task_id,
            'image_data': image_data,
            'filename': filename,
            'original_filename': filename,
            'is_regenerate': True
        }
        
        # 将任务放入队列
        image_processing_queue.put(task_data)
        
        print(f"[重新生成] 任务 {task_id} 已添加到队列，文件: {filename}")
        
        # 等待结果
        start_time = time.time()
        timeout = 60  # 60秒超时
        
        while time.time() - start_time < timeout:
            with results_lock:
                if task_id in processing_results:
                    result = processing_results.pop(task_id)
                    break
            time.sleep(0.5)
        else:
            # 超时处理
            print(f"[重新生成] 任务 {task_id} 处理超时")
            return jsonify({'success': False, 'message': '图片重新生成超时'}), 504
        
        # 处理结果
        # 确保result是字典类型，避免'list' object has no attribute 'get'错误
        if isinstance(result, list) and len(result) > 0:
            result = result[0]  # 取第一个结果作为默认结果
        elif not isinstance(result, dict):
            result = {'success': False, 'message': f'结果格式错误: {type(result).__name__}'}
        
        if result.get('success'):
            print(f"[重新生成] 任务 {task_id} 处理成功，文件: {filename}")
            # 从result['data']中获取正确的数据，而不是直接从result获取
            result_data = result.get('data', {})
            return jsonify({
                'success': True,
                'message': '图片重新生成成功',
                'data': {
                    'image': result_data.get('image'),
                    'text_content': result_data.get('text_content'),
                    'filename': result_data.get('filename')
                }
            })
        else:
            print(f"[重新生成] 任务 {task_id} 处理失败，文件: {filename}，错误信息: {result.get('message', '未知错误')}")
            error_msg = result.get('error', '生成失败')
            return jsonify({'success': False, 'message': error_msg}), 500
            
    except Exception as e:
        print(f"[重新生成] 接口错误: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器内部错误: {str(e)}'}), 500

def generate_ai_image():
    """
    AI图片生成接口（基于队列实现）
    接收客户端上传的图片，保存到临时文件后添加到处理队列，然后等待处理完成
    """
    # 生成唯一任务ID
    task_id = str(uuid.uuid4())
    print(f"[AI图片生成] 接收到新的图片生成请求，任务ID: {task_id}")
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            print(f"[AI图片生成] 任务 {task_id} - 请求数据为空或格式错误")
            return jsonify({
                'success': False,
                'message': '请求数据为空或格式错误'
            }), 400
        
        # 提取图片数组
        images = data.get('images', [])
        if not images or not isinstance(images, list):
            print(f"[AI图片生成] 任务 {task_id} - 未提供有效的图片数据")
            return jsonify({
                'success': False,
                'message': '未提供有效的图片数据'
            }), 400
        
        # 准备存储临时文件路径
        temp_filepaths = []
        
        try:
            # 初始化任务事件
            event = threading.Event()
            with results_lock:
                task_events[task_id] = {
                    'event': event,
                    'total': len(images)
                }
            
            # 循环处理每张图片，保存到临时文件并添加到队列
            for i, img in enumerate(images):
                try:
                    # 提取图片数据和文件名
                    if isinstance(img, dict) and 'data' in img:
                        image_data = img['data']
                        original_filename = img.get('filename', f'uploaded_image_{i+1}')
                    else:
                        # 兼容直接是base64字符串的情况
                        image_data = img
                        original_filename = f'uploaded_image_{i+1}'
                    
                    # 处理base64数据
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]  # 移除data:image/jpeg;base64,前缀
                    
                    # 创建临时目录保存图片
                    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'temp_ai_images')
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # 生成临时文件名
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                    temp_filename = f'{timestamp}.jpg'
                    temp_filepath = os.path.join(temp_dir, temp_filename)
                    temp_filepaths.append(temp_filepath)
                    
                    # 保存图片到临时文件
                    with open(temp_filepath, 'wb') as f:
                        f.write(base64.b64decode(image_data))
                    
                    print(f"[AI图片生成] 任务 {task_id} - 已保存临时图片文件: {temp_filepath}")
                    
                    # 创建任务对象并添加到队列
                    task = {
                        'task_id': task_id,
                        'temp_filepath': temp_filepath,
                        'original_filename': original_filename,
                        'index': i
                    }
                    image_processing_queue.put(task)
                    print(f"[AI图片生成] 任务 {task_id} - 图片 {i+1}/{len(images)} 已添加到处理队列")
                    
                except Exception as e:
                    error_msg = f"保存图片时出错: {str(e)}"
                    print(f"[AI图片生成] 任务 {task_id} - {error_msg}")
                    
                    # 直接添加错误结果
                    with results_lock:
                        if task_id not in processing_results:
                            processing_results[task_id] = []
                        processing_results[task_id].append({
                            'success': False,
                            'message': error_msg,
                            'filename': original_filename
                        })
                    
                    # 更新任务计数
                    with results_lock:
                        task_events[task_id]['total'] -= 1
                        if len(processing_results.get(task_id, [])) == task_events[task_id]['total']:
                            event.set()  # 如果所有任务都已处理或出错，触发完成事件
            
            # 等待处理完成（设置超时时间为300秒）
            print(f"[AI图片生成] 任务 {task_id} - 所有图片已提交到队列，等待处理完成...")
            completed = event.wait(timeout=300)
            
            # 获取处理结果
            with results_lock:
                all_results = processing_results.pop(task_id, [])
                task_events.pop(task_id, None)
            
            if not completed:
                print(f"[AI图片生成] 任务 {task_id} - 处理超时")
                # 如果超时，添加超时结果
                if not all_results:
                    all_results.append({
                        'success': False,
                        'message': '图片处理超时',
                        'filename': 'all'
                    })
            
            # 检查是否所有处理都成功
            all_success = all_results and all(result['success'] for result in all_results)
            
            print(f"[AI图片生成] 任务 {task_id} - 处理完成，成功: {all_success}, 结果数: {len(all_results)}")
            
            # 返回综合结果
            return jsonify({
                'success': all_success,
                'results': all_results
            })
            
        finally:
            print("[AI图片生成] 完成")
            
    except Exception as e:
        error_msg = f"服务器处理失败: {str(e)}"
        print(f"[AI图片生成] 任务 {task_id} - {error_msg}")
        
        # 清理任务相关资源
        with results_lock:
            processing_results.pop(task_id, None)
            task_events.pop(task_id, None)
        
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500