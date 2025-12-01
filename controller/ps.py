import os
import base64
from datetime import datetime
import cv2
import numpy as np
from flask import request, jsonify
from service.ps.watermark import remove_watermark_inpaint, add_watermark

def watermark_process_logic():
    """
    水印处理的核心逻辑函数
    循环调用remove_watermark_inpaint和add_watermark_to_image
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
        result_dir = 'd:/otherWorkspace/ins-robot/data/toRefine'
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