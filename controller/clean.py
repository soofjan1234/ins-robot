import os
import shutil

def clean_files():
    """清理所有待处理文件夹"""
    # 定义基础数据目录
    base_dir = 'd:/otherWorkspace/ins-robot/data'
    # 定义需要清理的文件夹
    folders = ['toGenerate', 'toPS', 'toRefine', 'toPublish']
    for folder in folders:
        path = os.path.join(base_dir, folder)
        if os.path.exists(path):
            shutil.rmtree(path)
        if not os.path.exists(path):
            os.makedirs(path)

    # 重建toPublish子文件夹
    publish_path = os.path.join(base_dir, 'toPublish')
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        day_path = os.path.join(publish_path, day)
        os.makedirs(day_path, exist_ok=True)