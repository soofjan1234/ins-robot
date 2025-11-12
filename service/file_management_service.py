import os
import shutil
from datetime import datetime, timedelta

class FileManagementService:
    """
    文件管理服务类，提供Instagram自动发布助手所需的文件管理功能
    """
    
    def __init__(self, base_dir="media"):
        """
        初始化文件管理服务
        
        Args:
            base_dir: 媒体文件的基础目录，默认为"media"
        """
        self.base_dir = base_dir
        self.weekday_folders = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    def create_weekly_folder_structure(self):
        """
        创建每周的文件夹结构
        - 首先删除旧的文件夹结构
        - 创建新的以日期范围命名的主文件夹
        - 在主文件夹内创建周一至周五的子文件夹
        
        Returns:
            str: 创建的主文件夹路径，如果创建失败则返回None
        """
        try:
            print(f"[文件管理服务] 开始创建每周文件夹结构")
            
            # 删除旧的media文件夹内容（如果存在）
            if os.path.exists(self.base_dir):
                print(f"[文件管理服务] 删除旧的文件夹结构: {self.base_dir}")
                shutil.rmtree(self.base_dir)
            
            # 创建base_dir
            os.makedirs(self.base_dir, exist_ok=True)
            
            # 计算当前周的日期范围
            start_date, end_date, folder_name = self._calculate_week_date_range()
            
            # 创建主文件夹
            main_folder_path = os.path.join(self.base_dir, folder_name)
            os.makedirs(main_folder_path, exist_ok=True)
            print(f"[文件管理服务] 创建主文件夹: {main_folder_path}")
            
            # 创建周一至周五的子文件夹
            for weekday in self.weekday_folders:
                subfolder_path = os.path.join(main_folder_path, weekday)
                os.makedirs(subfolder_path, exist_ok=True)
                print(f"[文件管理服务] 创建子文件夹: {subfolder_path}")
            
            print(f"[文件管理服务] 每周文件夹结构创建完成")
            return main_folder_path
        except Exception as e:
            print(f"[文件管理服务] 创建文件夹结构时出错: {e}")
            return None
    
    def _calculate_week_date_range(self):
        """
        计算当前周的日期范围（周一至周五）
        
        Returns:
            tuple: (start_date, end_date, folder_name)
        """
        # 获取当前日期
        today = datetime.now()
        
        # 计算本周一的日期
        days_since_monday = today.weekday()
        if days_since_monday == 0:  # 如果今天是周一
            start_date = today
        else:
            # 回溯到本周一
            start_date = today - timedelta(days=days_since_monday)
        
        # 计算本周五的日期
        end_date = start_date + timedelta(days=4)  # 周一+4天=周五
        
        # 格式化日期范围为MMDD-MMDD格式
        folder_name = f"{start_date.strftime('%m%d')}-{end_date.strftime('%m%d')}"
        
        return start_date, end_date, folder_name
    
    def get_today_folder_path(self):
        """
        获取今天对应的文件夹路径
        
        Returns:
            str: 今天的文件夹路径，如果文件夹不存在则返回None
        """
        try:
            # 获取当前日期对应的星期几
            today_weekday = datetime.now().strftime("%A")
            
            # 查找当前周的主文件夹
            current_week_folder = None
            if os.path.exists(self.base_dir):
                for folder in os.listdir(self.base_dir):
                    # 检查文件夹是否符合MMDD-MMDD格式
                    if len(folder) == 9 and folder[4] == '-':
                        try:
                            # 解析日期范围
                            start_str, end_str = folder.split('-')
                            start_date = datetime.strptime(start_str, "%m%d")
                            end_date = datetime.strptime(end_str, "%m%d")
                            
                            # 检查今天是否在这个日期范围内
                            today = datetime.now()
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
                                current_week_folder = folder
                                break
                        except ValueError:
                            continue
            
            if current_week_folder and today_weekday in self.weekday_folders:
                today_folder_path = os.path.join(self.base_dir, current_week_folder, today_weekday)
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
    
    def should_create_new_structure(self):
        """
        判断是否需要创建新的文件夹结构
        - 如果是周一，需要创建新的结构
        - 如果当前的文件夹结构不存在，需要创建新的结构
        
        Returns:
            bool: 是否需要创建新的文件夹结构
        """
        # 检查是否是周一
        is_monday = datetime.now().weekday() == 0
        
        # 检查文件夹结构是否存在
        structure_exists = False
        if os.path.exists(self.base_dir):
            # 查找是否有符合MMDD-MMDD格式的文件夹
            for folder in os.listdir(self.base_dir):
                if len(folder) == 9 and folder[4] == '-':
                    try:
                        # 验证文件夹名称格式
                        start_str, end_str = folder.split('-')
                        datetime.strptime(start_str, "%m%d")
                        datetime.strptime(end_str, "%m%d")
                        structure_exists = True
                        break
                    except ValueError:
                        continue
        
        # 周一或者文件夹结构不存在时，需要创建新结构
        return is_monday or not structure_exists