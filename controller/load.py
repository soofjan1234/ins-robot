import os
import base64
import json

def load_to_generate_images():
    """
    加载待生成文件夹中的图片
    返回图片列表和base64编码的图片数据
    """
    try:
        # 待生成图片文件夹路径
        to_generate_path = 'd:/otherWorkspace/ins-robot/data/toGenerate'
        
        if not os.path.exists(to_generate_path):
            return {
                'success': False,
                'message': '待生成图片文件夹不存在',
                'path': to_generate_path
            }, 404
        
        # 扫描文件夹中的图片文件
        files = os.listdir(to_generate_path)
        images = []
        
        for file in files:
            file_path = os.path.join(to_generate_path, file)
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
                    
                    print(f"[加载待生成图片] 成功加载图片: {file} ({len(image_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"[加载待生成图片] 处理图片 {file} 失败: {str(e)}")
                    continue
        
        print(f"[加载待生成图片] 总共加载了 {len(images)} 张图片")
        
        return {
            'success': True,
            'message': f'成功加载 {len(images)} 张待生成图片',
            'data': {
                'images': images,
                'total_images': len(images),
                'path': to_generate_path
            }
        }
        
    except Exception as e:
        print(f"[加载待生成图片] 加载失败: {str(e)}")
        return {
            'success': False,
            'message': f'加载待生成图片失败: {str(e)}'
        }, 500


def load_to_ps_imgs():
    """
    加载toPS文件夹中的图片
    返回图片列表和base64编码的图片数据
    """
    try:
        # toPS图片文件夹路径
        to_ps_path = 'd:/otherWorkspace/ins-robot/data/toPS'
        
        if not os.path.exists(to_ps_path):
            return {
                'success': False,
                'message': 'toPS图片文件夹不存在',
                'path': to_ps_path
            }, 404
        
        # 扫描文件夹中的图片文件
        files = os.listdir(to_ps_path)
        images = []
        
        for file in files:
            file_path = os.path.join(to_ps_path, file)
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
                    
                    print(f"[加载toPS图片] 成功加载图片: {file} ({len(image_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"[加载toPS图片] 处理图片 {file} 失败: {str(e)}")
                    continue
        
        print(f"[加载toPS图片] 总共加载了 {len(images)} 张图片")
        
        return {
            'success': True,
            'message': f'成功加载 {len(images)} 张toPS图片',
            'data': {
                'images': images,
                'total_images': len(images),
                'path': to_ps_path
            }
        }
        
    except Exception as e:
        print(f"[加载toPS图片] 加载失败: {str(e)}")
        return {
            'success': False,
            'message': f'加载toPS图片失败: {str(e)}'
        }, 500