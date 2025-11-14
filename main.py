from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
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
        # self.scheduler = BlockingScheduler()  # 移除定时调度器
    
    def initialize_folders(self):
        """
        初始化文件夹结构
        如果是周一或者文件夹不存在，则创建新的文件夹结构
        """
        print("[自动发布器] 检查文件夹结构...")
        if self.file_service.should_create_new_structure():
            self.file_service.create_weekly_folder_structure()
    
    def check_folder_structure(self):
        """
        检查文件夹结构
        """
        print("\n=== 检查文件夹结构 ===")
        
        # 获取当前周文件夹
        current_week = self.file_service.get_current_week_folder()
        print(f"当前周文件夹: {current_week}")
        
        # 检查data/media目录
        base_dir = self.file_service.base_dir
        print(f"基础目录: {base_dir}")
        
        if os.path.exists(base_dir):
            print("✅ 基础目录存在")
            
            # 列出所有周文件夹
            week_folders = []
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path) and '-' in item:
                    week_folders.append(item)
            
            if week_folders:
                print(f"找到 {len(week_folders)} 个周文件夹:")
                for folder in sorted(week_folders):
                    print(f"  - {folder}")
                    
                    # 检查子文件夹
                    folder_path = os.path.join(base_dir, folder)
                    subdirs = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
                    if subdirs:
                        print(f"    子文件夹: {', '.join(sorted(subdirs))}")
            else:
                print("❌ 未找到周文件夹")
        else:
            print("❌ 基础目录不存在")
            
        print("===================")
        """
        手动发布模式 - 根据当前日期执行对应的发布任务
        """
        from datetime import datetime
        import calendar
        
        today = datetime.now()
        weekday = today.weekday()  # 0=周一, 6=周日
        
        print(f"\n=== 手动发布模式 ===")
        print(f"今天是: {today.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"星期: {'周一' if weekday==0 else '周二' if weekday==1 else '周三' if weekday==2 else '周四' if weekday==3 else '周五' if weekday==4 else '周六' if weekday==5 else '周日'}")
        
        # 检查是否在工作日范围内（周一到周五）
        if weekday >= 5:  # 周六或周日
            print("❌ 今天是周末，不执行发布任务")
            return
        
        print(f"✅ 今天是工作日，开始执行发布任务...")
        
        # 执行发布任务
        self.publish_post()
        
        print("\n=== 手动发布完成 ===")
    
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
        运行手动发布模式
        """
        try:
            # 初始化文件夹
            self.initialize_folders()
            
            print("\n=== Instagram手动发布助手 ===")
            print("1. 手动发布今日内容")
            print("2. 检查文件夹结构")
            print("3. 退出")
            
            while True:
                choice = input("\n请选择操作 (1-3): ").strip()
                
                if choice == '1':
                    self.manual_publish()
                elif choice == '2':
                    self.check_folder_structure()
                elif choice == '3':
                    print("\n感谢使用，再见！")
                    break
                else:
                    print("无效选择，请重新输入")
                    
        except KeyboardInterrupt:
            print("\n\n用户中断程序，正在退出...")
        except Exception as e:
            print(f"\n发生错误: {e}")
        finally:
            print("程序已退出")

def main():
    """
    主函数
    """
    print("=== Instagram手动发布助手 ===")
    print("正在启动手动发布服务...")
    
    # 检查是否安装了必要的依赖
    try:
        import selenium
        # import apscheduler  # 移除定时任务依赖
    except ImportError as e:
        print(f"[错误] 缺少必要的依赖: {e}")
        print("请运行: pip install selenium webdriver-manager")
        return
    
    # 启动手动发布器
    auto_poster = InstagramAutoPoster()
    auto_poster.run()

if __name__ == "__main__":
    main()