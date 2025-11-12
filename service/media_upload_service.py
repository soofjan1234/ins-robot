from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time

class MediaUploadService:
    """
    媒体上传服务类，提供Instagram媒体上传相关功能
    """
    
    def __init__(self, driver):
        """
        初始化媒体上传服务
        
        Args:
            driver: Selenium WebDriver实例
        """
        self.driver = driver
    
    def click_create_post_button(self):
        """
        点击创建帖子按钮
        
        Returns:
            bool: 操作是否成功
        """
        try:
            print("[媒体上传服务] 正在查找创建帖子按钮...")
            
            # 尝试多种定位策略
            create_post_locators = [
                # 通过class组合定位
                (By.XPATH, "//div[contains(@class, '_aaqg') and contains(@class, '_aaqh')]")
            ]
            
            create_post_button = None
            for i, (by, value) in enumerate(create_post_locators):
                try:
                    print(f"[媒体上传服务] 尝试定位策略 {i+1}: {by}={value}")
                    create_post_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    print("[媒体上传服务] 成功找到创建帖子按钮")
                    break
                except Exception as e:
                    print(f"[媒体上传服务] 定位策略 {i+1} 失败: {e}")
            
            if create_post_button:
                create_post_button.click()
                print("[媒体上传服务] 成功点击创建帖子按钮")
                return True
            else:
                print("[媒体上传服务] 无法找到创建帖子按钮")
                return False
        except Exception as e:
            print(f"[媒体上传服务] 点击创建帖子按钮时出错: {e}")
            return False
    
    def wait_for_upload_interface(self, timeout=10):
        """
        等待上传界面加载完成
        
        Args:
            timeout: 等待超时时间（秒）
            
        Returns:
            bool: 上传界面是否准备就绪
        """
        try:
            print("[媒体上传服务] 等待上传界面加载...")
            
            # 检查文件输入元素是否存在
            file_input = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            
            print("[媒体上传服务] 上传界面加载完成")
            return True
        except Exception as e:
            print(f"[媒体上传服务] 上传界面加载超时或失败: {e}")
            return False
    
    def upload_media(self, file_path):
        """
        上传媒体文件
        
        Args:
            file_path: 媒体文件的绝对路径
            
        Returns:
            bool: 上传是否成功
        """
        try:
            print(f"[媒体上传服务] 准备上传文件: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"[媒体上传服务] 错误: 文件 {file_path} 不存在")
                return False
            
            # 查找文件输入元素
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            
            # 上传文件
            file_input.send_keys(file_path)
            print("[媒体上传服务] 文件上传开始")
            
            # 等待上传完成（根据网络情况可能需要调整等待时间）
            time.sleep(5)
            print("[媒体上传服务] 文件上传完成")
            return True
        except Exception as e:
            print(f"[媒体上传服务] 上传文件时出错: {e}")
            return False
    
    def go_to_next_step(self):
        """
        点击下一步按钮，进入下一上传阶段
        
        Returns:
            bool: 操作是否成功
        """
        try:
            print("[媒体上传服务] 查找下一步按钮...")
            
            # 尝试多种定位策略
            next_button_locators = [
                # 通过文本定位下一步按钮
                (By.XPATH, "//button[span[text()='下一步'] or span[text()='Next']]"),
                # 通过class组合定位
                (By.XPATH, "//div[contains(@class, '_ac7b') and contains(@class, '_ac7c')]//button")
            ]
            
            next_button = None
            for i, (by, value) in enumerate(next_button_locators):
                try:
                    print(f"[媒体上传服务] 尝试定位策略 {i+1}: {by}={value}")
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    print("[媒体上传服务] 成功找到下一步按钮")
                    break
                except Exception as e:
                    print(f"[媒体上传服务] 定位策略 {i+1} 失败: {e}")
            
            if next_button:
                next_button.click()
                print("[媒体上传服务] 成功点击下一步按钮")
                # 等待页面切换
                time.sleep(2)
                return True
            else:
                print("[媒体上传服务] 无法找到下一步按钮")
                return False
        except Exception as e:
            print(f"[媒体上传服务] 点击下一步按钮时出错: {e}")
            return False
    
    def click_share_button(self):
        """
        点击分享按钮，发布帖子
        
        Returns:
            bool: 操作是否成功
        """
        try:
            print("[媒体上传服务] 查找分享按钮...")
            
            # 尝试多种定位策略
            share_button_locators = [
                # 通过文本定位分享按钮
                (By.XPATH, "//button[span[text()='分享' or text()='Share']]"),
                # 通过class组合定位
                (By.XPATH, "//div[contains(@class, '_ac7b') and contains(@class, '_ac7c')]//button[contains(@class, '_acan')]")
            ]
            
            share_button = None
            for i, (by, value) in enumerate(share_button_locators):
                try:
                    print(f"[媒体上传服务] 尝试定位策略 {i+1}: {by}={value}")
                    share_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    print("[媒体上传服务] 成功找到分享按钮")
                    break
                except Exception as e:
                    print(f"[媒体上传服务] 定位策略 {i+1} 失败: {e}")
            
            if share_button:
                share_button.click()
                print("[媒体上传服务] 成功点击分享按钮")
                # 等待发布完成
                time.sleep(5)
                return True
            else:
                print("[媒体上传服务] 无法找到分享按钮")
                return False
        except Exception as e:
            print(f"[媒体上传服务] 点击分享按钮时出错: {e}")
            return False