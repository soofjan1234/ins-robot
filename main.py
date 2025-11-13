from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import time
import random
import os

# 导入服务类
from ins_robot.login import InstagramLoginService, get_chrome_options, create_webdriver
from ins_robot.file_management_service import FileManagementService
from ins_robot.media_upload_service import MediaUploadService
from ins_robot.text_processing_service import TextProcessingService

class InstagramAutoPoster:
    """
    Instagram自动发布主类
    """
    
    def __init__(self):
        """
        初始化自动发布器
        """
        self.file_service = FileManagementService()
        self.scheduler = BlockingScheduler()
    
    def initialize_folders(self):
        """
        初始化文件夹结构
        如果是周一或者文件夹不存在，则创建新的文件夹结构
        """
        print("[自动发布器] 检查文件夹结构...")
        if self.file_service.should_create_new_structure():
            self.file_service.create_weekly_folder_structure()
    
    def schedule_tasks(self):
        """
        安排定时任务
        - 周一早上8点创建新的文件夹结构
        - 周一至周五12:00-14:00之间随机时间发布帖子
        """
        # 每周一早上8点创建文件夹结构
        self.scheduler.add_job(
            self.file_service.create_weekly_folder_structure,
            CronTrigger(day_of_week='0', hour=8, minute=0),
            id='create_folder_structure',
            name='创建每周文件夹结构'
        )
        print("[自动发布器] 已安排每周一早上8点创建文件夹结构的任务")
        
        # 周一至周五每天在12:00-14:00之间随机时间发布帖子
        for day in range(5):  # 0=周一, 4=周五
            # 生成随机分钟数（0-120分钟，即2小时）
            random_minutes = random.randint(0, 120)
            
            # 添加任务
            self.scheduler.add_job(
                self.publish_post,
                CronTrigger(day_of_week=str(day), hour=12, minute=random_minutes),
                id=f'publish_post_day_{day}',
                name=f'发布帖子（{"周一" if day==0 else "周二" if day==1 else "周三" if day==2 else "周四" if day==3 else "周五"}）'
            )
            print(f"[自动发布器] 已安排{"周一" if day==0 else "周二" if day==1 else "周三" if day==2 else "周四" if day==3 else "周五"} {12 + random_minutes // 60}:{random_minutes % 60:02d} 发布帖子")
    
    def publish_post(self):
        """
        执行发布帖子的完整流程
        """
        driver = None
        try:
            print("\n[自动发布器] 开始执行发布任务...")
            
            # 1. 初始化浏览器
            print("[自动发布器] 初始化浏览器...")
            options = get_chrome_options(headless=False)
            driver = create_webdriver(options)
            
            # 2. 登录Instagram
            print("[自动发布器] 登录Instagram...")
            login_service = InstagramLoginService()
            login_success = login_service.login(driver)
            
            if not login_success:
                print("[自动发布器] 登录失败，取消发布任务")
                return
            
            # 等待页面完全加载
            print("[自动发布器] 等待页面加载完成...")
            time.sleep(5)
            
            # 3. 获取今天的媒体文件
            print("[自动发布器] 获取今天的媒体文件...")
            media_files = self.file_service.get_media_files_for_today()
            
            if not media_files["images"]:
                print("[自动发布器] 未找到图片文件，取消发布任务")
                return
            
            # 4. 初始化服务
            media_service = MediaUploadService(driver)
            text_service = TextProcessingService(driver)
            
            # 5. 点击创建帖子按钮
            print("[自动发布器] 点击创建帖子按钮...")
            if not media_service.click_create_post_button():
                print("[自动发布器] 点击创建帖子按钮失败")
                return
            
            # 6. 等待上传界面
            print("[自动发布器] 等待上传界面...")
            media_service.wait_for_upload_interface()
            
            # 7. 上传第一张图片
            image_path = media_files["images"][0]
            print(f"[自动发布器] 上传图片: {image_path}")
            if not media_service.upload_media(image_path):
                print("[自动发布器] 上传图片失败")
                return
            
            # 8. 点击下一步
            print("[自动发布器] 点击下一步...")
            if not media_service.go_to_next_step():
                print("[自动发布器] 点击下一步失败")
                return
            
            # 9. 再次点击下一步
            print("[自动发布器] 再次点击下一步...")
            if not media_service.go_to_next_step():
                print("[自动发布器] 再次点击下一步失败")
                return
            
            # 10. 如果有文案文件，处理并填充
            if media_files["texts"]:
                text_path = media_files["texts"][0]
                print(f"[自动发布器] 处理文案文件: {text_path}")
                text_content = self.file_service.read_text_file(text_path)
                
                if text_content:
                    print("[自动发布器] 等待文本框准备就绪...")
                    text_service.wait_for_textarea_ready()
                    
                    print("[自动发布器] 处理文本内容...")
                    processed_content = text_service.process_hashtags(text_content)
                    
                    print("[自动发布器] 填充文本框...")
                    text_service.fill_caption_textarea(processed_content)
            
            # 11. 点击分享按钮发布
            print("[自动发布器] 点击分享按钮发布...")
            if not media_service.click_share_button():
                print("[自动发布器] 点击分享按钮失败")
                return
            
            print("[自动发布器] 发布成功！")
            
        except Exception as e:
            print(f"[自动发布器] 发布过程中发生错误: {e}")
        finally:
            # 关闭浏览器
            if driver:
                print("[自动发布器] 关闭浏览器")
                driver.quit()
    
    def run(self):
        """
        运行自动发布器
        """
        try:
            # 初始化文件夹
            self.initialize_folders()
            
            # 安排定时任务
            self.schedule_tasks()
            
            print("\n[自动发布器] 定时任务已启动，按Ctrl+C停止...")
            
            # 启动调度器
            self.scheduler.start()
            
        except KeyboardInterrupt:
            print("\n[自动发布器] 用户中断程序")
        except Exception as e:
            print(f"\n[自动发布器] 发生错误: {e}")
        finally:
            # 关闭调度器
            if hasattr(self, 'scheduler'):
                self.scheduler.shutdown()
            print("[自动发布器] 程序已退出")

def main():
    """
    主函数
    """
    print("=== Instagram自动发布助手 ===")
    print("正在启动自动发布服务...")
    
    # 检查是否安装了必要的依赖
    try:
        import selenium
        import apscheduler
    except ImportError as e:
        print(f"[错误] 缺少必要的依赖: {e}")
        print("请运行: pip install selenium apscheduler webdriver-manager")
        return
    
    # 启动自动发布器
    auto_poster = InstagramAutoPoster()
    auto_poster.run()

if __name__ == "__main__":
    main()