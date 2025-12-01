import os
import shutil
from flask import request, jsonify

def organize_images_api():
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
        base_media_path = 'd:/otherWorkspace/ins-robot/data/toPublish'
        ps_result_path = 'd:/otherWorkspace/ins-robot/data/toRefine'
        
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