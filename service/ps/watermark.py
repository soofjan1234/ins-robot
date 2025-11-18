import cv2
import numpy as np
from PIL import Image
import os

# 设置基础目录
base_dir = 'd:/otherWorkspace/ins-robot/service/ps'
watermark_image = os.path.join(base_dir, 'watermark.PNG')

def add_watermark(original_image, output_path):
    """
    将watermark_image作为水印添加到original_image图片上
    """

    # 检查文件是否存在
    if not os.path.exists(original_image):
        print('❌ 原图文件不存在')
        return False
        
    if not os.path.exists(watermark_image):
        print('❌ 水印文件不存在')
        return False

    # 打开图片
    with Image.open(original_image) as img:
        with Image.open(watermark_image) as watermark:
            
            # 转换为RGBA模式
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            
            # 调整水印大小
            img_width, img_height = img.size
            watermark_width = int(img_width * 0.2)
            watermark_height = int(watermark.height * (watermark_width / watermark.width))
            
            watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # 计算位置（右上角）
            margin = 20
            x = img_width - 2 * watermark_width - margin
            y = margin
            
            # 创建透明层并粘贴水印
            transparent = Image.new('RGBA', img.size, (255, 255, 255, 0))
            transparent.paste(watermark, (x, y), watermark)
            
            # 合并图片
            result = Image.alpha_composite(img, transparent)
            
            # 转换回RGB并保存
            result = result.convert('RGB')
            result.save(output_path, 'JPEG', quality=95)
            
            print('✅ 水印添加成功！')
            print(f'输出文件: {output_path}')
            print(f'文件大小: {os.path.getsize(output_path) / 1024:.1f} KB')
            return True
    return False

def remove_watermark_inpaint(original_image, output_path):
    """
    使用inpaint算法移除original_image图片上的水印
    """
    # 检查文件是否存在
    if not os.path.exists(original_image):
        print('❌ 原图文件不存在')
        return False
        
    """使用OpenCV的内容感知填充"""
    img = cv2.imread(original_image)
    
    # 创建水印区域的遮罩（需要根据实际水印位置调整）
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    # 假设水印在右下角，大小约150x150
    h, w = img.shape[:2]
    mask[h-150:h, w-150:w] = 255
    
    # 使用TELEA算法进行修复
    result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    
    cv2.imwrite(output_path, result)
    print('✅ 水印移除成功！')
    print(f'输出文件: {output_path}')
    print(f'文件大小: {os.path.getsize(output_path) / 1024:.1f} KB')
    return True