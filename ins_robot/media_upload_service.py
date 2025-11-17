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
                # 通过span文本"创建"定位
                (By.XPATH, "//span[text()='创建']"),
                (By.XPATH, "//span[text()='New post']"),
                # 通过包含"创建"文本的div容器定位
                (By.XPATH, "//div[.//span[text()='创建']]"),
                (By.XPATH, "//div[.//span[text()='New post']]"),
                # 通过最外层div的特定class定位
                (By.XPATH, "//div[contains(@class, 'x9f619') and .//span[text()='创建']]"),
                (By.XPATH, "//div[contains(@class, 'x9f619') and .//span[text()='New post']]")
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
            
            # 尝试多种定位策略 - 基于实际页面结构优化
            next_button_locators = [
                # 通过文本"继续"定位（根据你提供的实际页面元素）
                (By.XPATH, "//*[text()='继续']"),
                (By.XPATH, "//div[contains(@class, 'x1i10hfl') and text()='继续']"),
                # 通过文本"Next"定位
                (By.XPATH, "//button[contains(., 'Next')]"),
                # 通过特定的class组合定位（基于你提供的class列表）
                (By.XPATH, "//div[contains(@class, 'x1i10hfl') and contains(@class, 'xjqpnuy') and @role='button']"),
                # 通过aria-label属性定位
                (By.XPATH, "//button[@aria-label='Next' or @aria-label='继续']"),
                # 通过按钮的文本内容模糊匹配
                (By.XPATH, "//button[contains(text(), 'Next') or contains(text(), '继续')]"),
                # CSS选择器定位
                (By.CSS_SELECTOR, "div[role='button'][tabindex='0']"),
                # 通过父容器和按钮组合定位
                (By.XPATH, "//div[contains(@class, 'x9f619')]//button[contains(@class, '_acan')]"),
            ]
            
            next_button = None
            for i, (by, value) in enumerate(next_button_locators):
                try:
                    print(f"[媒体上传服务] 尝试定位策略 {i+1}: {by}={value}")
                    next_button = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    print(f"[媒体上传服务] 成功找到下一步按钮，使用策略 {i+1}")
                    break
                except Exception as e:
                    print(f"[媒体上传服务] 定位策略 {i+1} 失败: {e}")
            
            if next_button:
                # 滚动到元素位置确保可见
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                
                # 尝试多种点击方式
                try:
                    next_button.click()
                    print("[媒体上传服务] 成功点击下一步按钮（普通点击）")
                except Exception:
                    try:
                        # JavaScript点击作为备选方案
                        self.driver.execute_script("arguments[0].click();", next_button)
                        print("[媒体上传服务] 成功点击下一步按钮（JavaScript点击）")
                    except Exception as e:
                        print(f"[媒体上传服务] 点击按钮失败: {e}")
                        return False
                
                # 等待页面切换
                time.sleep(3)
                return True
            else:
                print("[媒体上传服务] 无法找到下一步按钮，所有定位策略均失败")
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
            
            # 基于a.txt中的实际HTML结构优化 - 只使用可靠的属性
            share_button_locators = [
                # 通过文本内容和可靠属性定位 - 最可靠的方式
                (By.XPATH, "//div[@role='button' and @tabindex='0' and text()='分享']"),
                (By.XPATH, "//div[@role='button' and @tabindex='0' and text()='Share']"),
                # 通过文本内容定位（不依赖class）
                (By.XPATH, "//*[text()='分享']"),
                (By.XPATH, "//*[text()='Share']"),
                # 通过role和tabindex组合定位（文本内容作为子元素）
                (By.XPATH, "//div[@role='button' and @tabindex='0']//*[text()='分享']"),
                (By.XPATH, "//div[@role='button' and @tabindex='0']//*[text()='Share']"),
                # 通过父元素和可靠属性定位
                (By.XPATH, "//div[@role='button' and @tabindex='0'][last()]"),  # 最后一个分享按钮
            ]
            
            share_button = None
            for i, (by, value) in enumerate(share_button_locators):
                try:
                    print(f"[媒体上传服务] 尝试定位策略 {i+1}: {by}={value}")
                    share_button = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    print(f"[媒体上传服务] 成功找到分享按钮，使用策略 {i+1}")
                    # 验证元素文本内容
                    element_text = share_button.text.strip()
                    print(f"[媒体上传服务] 分享按钮文本内容: '{element_text}'")
                    break
                except Exception as e:
                    print(f"[媒体上传服务] 定位策略 {i+1} 失败: {e}")
            
            if share_button:
                # 滚动到元素位置确保可见
                self.driver.execute_script("arguments[0].scrollIntoView(true);", share_button)
                time.sleep(0.5)
                
                # 验证元素是否在视图中且可点击
                if share_button.is_displayed() and share_button.is_enabled():
                    print("[媒体上传服务] 分享按钮可见且可用")
                else:
                    print("[媒体上传服务] 警告: 分享按钮可能不可见或不可用")
                
                # 尝试多种点击方式
                try:
                    share_button.click()
                    print("[媒体上传服务] 成功点击分享按钮（普通点击）")
                except Exception:
                    try:
                        # JavaScript点击作为备选方案
                        self.driver.execute_script("arguments[0].click();", share_button)
                        print("[媒体上传服务] 成功点击分享按钮（JavaScript点击）")
                    except Exception as e:
                        print(f"[媒体上传服务] 点击分享按钮失败: {e}")
                        return False
                
                # 等待发布完成
                print("[媒体上传服务] 等待发布完成...")
                time.sleep(10)  # 增加等待时间确保发布完成
                return True
            else:
                print("[媒体上传服务] 无法找到分享按钮，所有定位策略均失败")
                return False
        except Exception as e:
            print(f"[媒体上传服务] 点击分享按钮时出错: {e}")
            return False