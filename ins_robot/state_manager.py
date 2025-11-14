import json
import os
from datetime import datetime, date

class StateManager:
    """状态管理器，用于处理程序重启后的恢复功能"""
    
    def __init__(self, state_file="state.json"):
        """
        初始化状态管理器
        
        Args:
            state_file: 状态文件路径，默认为state.json
        """
        self.state_file = state_file
        self.state = self.load_state()
    
    def load_state(self):
        """
        从文件加载状态
        
        Returns:
            dict: 状态字典，如果文件不存在或损坏则返回默认状态
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    print(f"[状态管理] 成功加载状态文件: {self.state_file}")
                    return state
        except Exception as e:
            print(f"[状态管理] 加载状态文件时出错: {e}")
        
        # 返回默认状态
        return self.get_default_state()
    
    def get_default_state(self):
        """
        获取默认状态
        
        Returns:
            dict: 默认状态字典
        """
        return {
            "last_run_date": None,
            "current_week_folder": None,
            "completed_posts": [],
            "failed_posts": [],
            "last_post_index": 0,
            "total_posts": 0,
            "is_week_complete": False,
            "last_update_time": None
        }
    
    def save_state(self):
        """
        保存当前状态到文件
        """
        try:
            # 更新最后更新时间
            self.state["last_update_time"] = datetime.now().isoformat()
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            print(f"[状态管理] 状态已保存到文件: {self.state_file}")
        except Exception as e:
            print(f"[状态管理] 保存状态文件时出错: {e}")
    
    def update_last_run_date(self, date_str=None):
        """
        更新最后运行日期
        
        Args:
            date_str: 日期字符串，如果为None则使用当前日期
        """
        if date_str is None:
            date_str = date.today().isoformat()
        self.state["last_run_date"] = date_str
        self.save_state()
    
    def update_week_folder(self, week_folder):
        """
        更新当前周文件夹
        
        Args:
            week_folder: 周文件夹路径
        """
        self.state["current_week_folder"] = week_folder
        self.save_state()
    
    def add_completed_post(self, post_info):
        """
        添加已完成的发布任务
        
        Args:
            post_info: 发布任务信息字典
        """
        self.state["completed_posts"].append({
            "date": date.today().isoformat(),
            "weekday": datetime.now().strftime("%A"),
            "post_info": post_info,
            "completed_at": datetime.now().isoformat()
        })
        self.save_state()
    
    def add_failed_post(self, post_info, error_msg):
        """
        添加失败的发布任务
        
        Args:
            post_info: 发布任务信息字典
            error_msg: 错误信息
        """
        self.state["failed_posts"].append({
            "date": date.today().isoformat(),
            "weekday": datetime.now().strftime("%A"),
            "post_info": post_info,
            "error_msg": error_msg,
            "failed_at": datetime.now().isoformat()
        })
        self.save_state()
    
    def update_post_progress(self, current_index, total_posts):
        """
        更新发布进度
        
        Args:
            current_index: 当前发布索引
            total_posts: 总发布数量
        """
        self.state["last_post_index"] = current_index
        self.state["total_posts"] = total_posts
        self.save_state()
    
    def mark_week_complete(self, is_complete=True):
        """
        标记周任务是否完成
        
        Args:
            is_complete: 是否完成
        """
        self.state["is_week_complete"] = is_complete
        self.save_state()
    
    def should_continue_from_last_position(self):
        """
        判断是否应该从上次的断点继续执行
        
        Returns:
            bool: 是否应该继续执行
        """
        # 检查是否有最后运行日期
        if not self.state["last_run_date"]:
            return False
        
        # 检查最后运行日期是否是今天
        last_date = date.fromisoformat(self.state["last_run_date"])
        today = date.today()
        
        if last_date != today:
            return False
        
        # 检查是否已完成今天的所有任务
        if self.state["is_week_complete"]:
            return False
        
        # 检查是否有未完成的任务
        return self.state["last_post_index"] < self.state["total_posts"]
    
    def get_today_progress(self):
        """
        获取今天的发布进度
        
        Returns:
            dict: 包含进度信息的字典
        """
        today = date.today().isoformat()
        
        # 获取今天已完成的任务
        today_completed = [post for post in self.state["completed_posts"] 
                           if post["date"] == today]
        
        # 获取今天失败的任务
        today_failed = [post for post in self.state["failed_posts"] 
                       if post["date"] == today]
        
        return {
            "completed_count": len(today_completed),
            "failed_count": len(today_failed),
            "last_post_index": self.state["last_post_index"],
            "total_posts": self.state["total_posts"],
            "progress_percentage": (self.state["last_post_index"] / max(self.state["total_posts"], 1)) * 100
        }
    
    def get_recovery_info(self):
        """
        获取恢复执行所需的信息
        
        Returns:
            dict: 恢复信息字典
        """
        if not self.should_continue_from_last_position():
            return None
        
        return {
            "last_post_index": self.state["last_post_index"],
            "total_posts": self.state["total_posts"],
            "current_week_folder": self.state["current_week_folder"],
            "progress": self.get_today_progress()
        }
    
    def reset_week_state(self):
        """
        重置周状态（新的一周开始时调用）
        """
        self.state["completed_posts"] = []
        self.state["failed_posts"] = []
        self.state["last_post_index"] = 0
        self.state["total_posts"] = 0
        self.state["is_week_complete"] = False
        self.state["current_week_folder"] = None
        self.save_state()
    
    def print_state_summary(self):
        """
        打印状态摘要信息
        """
        print("\n=== 状态摘要 ===")
        print(f"最后运行日期: {self.state['last_run_date']}")
        print(f"当前周文件夹: {self.state['current_week_folder']}")
        print(f"已完成任务数: {len(self.state['completed_posts'])}")
        print(f"失败任务数: {len(self.state['failed_posts'])}")
        print(f"最后发布索引: {self.state['last_post_index']}")
        print(f"总发布数量: {self.state['total_posts']}")
        print(f"周任务完成: {self.state['is_week_complete']}")
        print(f"最后更新时间: {self.state['last_update_time']}")
        
        if self.should_continue_from_last_position():
            print("\n[状态管理] 检测到未完成的任务，可以从断点继续执行")
            recovery_info = self.get_recovery_info()
            print(f"[状态管理] 恢复信息: {recovery_info}")
        else:
            print("\n[状态管理] 无需恢复执行")
        print("================\n")