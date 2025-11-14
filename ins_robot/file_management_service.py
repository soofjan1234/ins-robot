import os
import shutil
from datetime import datetime, timedelta

class FileManagementService:
    """
    文件管理服务类，提供Instagram自动发布助手所需的文件管理功能
    """
    
    def __init__(self, base_dir="data/media"):
        """
        初始化文件管理服务
        
        Args:
            base_dir: 媒体文件的基础目录，默认为"data/media"
        """
        self.base_dir = base_dir
        self.weekday_folders = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    def create_weekly_folder_structure(self):
        """
        创建每周的文件夹结构
        - 首先删除旧的文件夹内容（如果存在）
        - 直接在base_dir下创建周一至周五的子文件夹
        
        Returns:
            str: 创建的base_dir路径，如果创建失败则返回None
        """
        try:
            print(f"[文件管理服务] 开始创建每周文件夹结构")
            
            # 删除旧的media文件夹内容（如果存在）
            if os.path.exists(self.base_dir):
                print(f"[文件管理服务] 删除旧的media文件夹内容（如果存在）: {self.base_dir}")
                shutil.rmtree(self.base_dir)
            
            # 创建base_dir
            os.makedirs(self.base_dir, exist_ok=True)
            print(f"[文件管理服务] 创建基础目录: {self.base_dir}")
            
            # 直接在base_dir下创建周一至周五的子文件夹
            for weekday in self.weekday_folders:
                weekday_path = os.path.join(self.base_dir, weekday)
                os.makedirs(weekday_path, exist_ok=True)
                print(f"[文件管理服务] 创建星期文件夹: {weekday_path}")
            
            print(f"[文件管理服务] 每周文件夹结构创建完成")
            return self.base_dir
        except Exception as e:
            print(f"[文件管理服务] 创建文件夹结构时出错: {e}")
            return None
    

    
    def get_today_folder_path(self):
        """
        获取今天对应的文件夹路径
        
        Returns:
            str: 今天的文件夹路径，如果文件夹不存在则返回None
        """
        try:
            # 获取当前日期对应的星期几
            today_weekday = datetime.now().strftime("%A")
            
            # 直接检查星期文件夹是否存在
            if today_weekday in self.weekday_folders:
                today_folder_path = os.path.join(self.base_dir, today_weekday)
                if os.path.exists(today_folder_path):
                    print(f"[文件管理服务] 找到今天的文件夹路径: {today_folder_path}")
                    return today_folder_path
            
            print(f"[文件管理服务] 未找到今天的文件夹路径")
            return None
        except Exception as e:
            print(f"[文件管理服务] 获取今天文件夹路径时出错: {e}")
            return None
    
    def get_media_files_for_today(self):
        """
        获取今天需要发布的媒体文件（图片和文案）
        
        Returns:
            dict: 包含图片和文案文件路径的字典，格式为{"images": [图片路径列表], "texts": [文案路径列表]}
        """
        try:
            today_folder = self.get_today_folder_path()
            if not today_folder:
                return {"images": [], "texts": []}
            
            images = []
            texts = []
            
            # 遍历今天的文件夹
            for file in os.listdir(today_folder):
                file_path = os.path.join(today_folder, file)
                
                # 检查是否为文件
                if os.path.isfile(file_path):
                    # 检查文件扩展名
                    _, ext = os.path.splitext(file.lower())
                    
                    if ext in [".jpg", ".jpeg", ".png"]:
                        images.append(file_path)
                    elif ext == ".txt":
                        texts.append(file_path)
            
            print(f"[文件管理服务] 找到 {len(images)} 个图片文件和 {len(texts)} 个文案文件")
            return {"images": images, "texts": texts}
        except Exception as e:
            print(f"[文件管理服务] 获取媒体文件时出错: {e}")
            return {"images": [], "texts": []}
    
    def read_text_file(self, file_path):
        """
        读取文本文件内容
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            str: 文件内容，如果读取失败则返回None
        """
        try:
            if not os.path.exists(file_path):
                print(f"[文件管理服务] 文件不存在: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[文件管理服务] 成功读取文件内容: {file_path}")
                return content
        except Exception as e:
            print(f"[文件管理服务] 读取文件时出错: {e}")
            return None
    
    def check_folder_structure(self):
        """
        检查文件夹结构
        - 显示基础目录信息
        - 列出所有星期文件夹
        - 显示每个文件夹中的文件数量
        """
        try:
            print(f"[文件管理服务] 文件夹结构检查:")
            print(f"[文件管理服务] 基础目录: {self.base_dir}")
            
            if not os.path.exists(self.base_dir):
                print(f"[文件管理服务] 基础目录不存在")
                return
            
            # 检查星期文件夹
            for weekday in self.weekday_folders:
                weekday_path = os.path.join(self.base_dir, weekday)
                if os.path.exists(weekday_path):
                    # 统计文件数量
                    files = [f for f in os.listdir(weekday_path) if os.path.isfile(os.path.join(weekday_path, f))]
                    print(f"[文件管理服务] {weekday}: {len(files)} 个文件")
                else:
                    print(f"[文件管理服务] {weekday}: 文件夹不存在")
                    
        except Exception as e:
            print(f"[文件管理服务] 检查文件夹结构时出错: {e}")

    def should_create_new_structure(self):
        """
        判断是否需要创建新的文件夹结构
        - 如果是周一，需要创建新的结构
        - 如果星期文件夹不存在，需要创建新的结构
        
        Returns:
            bool: 是否需要创建新的文件夹结构
        """
        # 检查是否是周一
        is_monday = datetime.now().weekday() == 0
        
        # 检查星期文件夹是否存在
        structure_exists = False
        if os.path.exists(self.base_dir):
            # 检查是否至少有一个星期文件夹存在
            existing_folders = os.listdir(self.base_dir)
            for weekday in self.weekday_folders:
                if weekday in existing_folders:
                    structure_exists = True
                    break
        
        # 周一或者文件夹结构不存在时，需要创建新结构
        return is_monday or not structure_exists
    
    def get_current_week_folder(self):
        """
        获取当前的周文件夹路径
        
        Returns:
            str: 当前周文件夹路径，如果不存在则返回None
        """
        try:
            if not os.path.exists(self.base_dir):
                return None
            
            today = datetime.now()
            
            # 查找当前周的主文件夹
            for folder in os.listdir(self.base_dir):
                # 检查文件夹是否符合MMDD-MMDD格式
                if len(folder) == 9 and folder[4] == '-':
                    try:
                        # 解析日期范围
                        start_str, end_str = folder.split('-')
                        start_date = datetime.strptime(start_str, "%m%d")
                        end_date = datetime.strptime(end_str, "%m%d")
                        
                        # 检查今天是否在这个日期范围内
                        # 调整年份进行比较
                        start_date = start_date.replace(year=today.year)
                        end_date = end_date.replace(year=today.year)
                        
                        # 处理跨年情况
                        if end_date < start_date:
                            if today.month >= 11 and start_date.month <= 2:
                                start_date = start_date.replace(year=today.year - 1)
                            elif today.month <= 2 and end_date.month >= 11:
                                end_date = end_date.replace(year=today.year + 1)
                        
                        if start_date <= today <= end_date:
                            week_folder_path = os.path.join(self.base_dir, folder)
                            print(f"[文件管理服务] 找到当前周文件夹: {week_folder_path}")
                            return week_folder_path
                            
                    except ValueError:
                        continue
            
            print("[文件管理服务] 未找到当前周文件夹")
            return None
            
        except Exception as e:
            print(f"[文件管理服务] 获取当前周文件夹时出错: {e}")
            return None