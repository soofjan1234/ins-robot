from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os

class InstagramLoginService:
    """
    Instagram登录服务类，提供Instagram账号登录功能
    """
    
    def __init__(self):
        """
        初始化登录服务
        """
        # 加载环境变量
        load_dotenv()
        # 从环境变量获取默认账号密码（可选）
        self.default_username = os.getenv('IG_USERNAME')
        self.default_password = os.getenv('IG_PASSWORD')
    
    def login(self, driver, username=None, password=None):
        """
        登录Instagram
        
        Args:
            driver: Selenium WebDriver实例
            username: Instagram用户名（可选，如果不提供则使用环境变量中的值）
            password: Instagram密码（可选，如果不提供则使用环境变量中的值）
            
        Returns:
            bool: 登录是否成功
            
        Raises:
            ValueError: 如果没有提供用户名或密码
            Exception: 登录过程中的其他错误
        """
        # 使用提供的账号密码或默认值
        username = username or self.default_username
        password = password or self.default_password
        
        if not username or not password:
            raise ValueError("必须提供Instagram用户名和密码")
        
        try:
            print(f"[登录服务] 正在使用账号 {username} 登录Instagram...")
            
            # 打开Instagram网站
            driver.get("https://www.instagram.com/")
            
            # 等待页面加载完成
            time.sleep(3)
            
            # 检查是否已经登录
            if self._verify_login_success(driver):
                print(f"[登录服务] 检测到账号 {username} 已经处于登录状态，无需重复登录！")
                return True
            
            # 如果未登录，则填写登录表单
            print("[登录服务] 未检测到登录状态，继续登录流程...")
            self._fill_login_form(driver, username, password)
            
            # 点击登录按钮
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # 验证登录是否成功
            success = self._verify_login_success(driver)
            
            if success:
                # 处理登录后的通知提示
                print(f"[登录服务] 账号 {username} 登录成功！")
            else:
                print(f"[登录服务] 账号 {username} 登录失败")
                
            return success
            
        except Exception as e:
            print(f"[登录服务] 登录过程中发生错误: {e}")
            raise
    
    
    def _fill_login_form(self, driver, username, password):
        """
        填写登录表单，使用多种定位策略以提高兼容性
        """
        print("[登录服务] 等待登录表单加载...")
        
        # 尝试多种定位方式
        username_input = None
        password_input = None
        
        # 策略: 通过NAME定位
        try:
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = driver.find_element(By.NAME, "password")
            print("[登录服务] 成功通过NAME定位登录表单")
        except Exception:
            print("[登录服务] 通过NAME定位失败，尝试通过XPATH定位...")
            
        
        # 确保元素可交互后再输入
        if username_input and password_input:
            # 清除可能存在的默认值
            username_input.clear()
            password_input.clear()
            
            # 输入用户名和密码
            username_input.send_keys(username)
            password_input.send_keys(password)
        else:
            raise Exception("[登录服务] 无法定位登录表单元素")
    
    def _verify_login_success(self, driver):
        """
        验证登录是否成功，使用多种验证方法
        """
        print("[登录服务] 正在验证登录状态...")
        
        
        # 方法: 检查是否有主页元素（基于1.txt中的HTML结构）
        try:
            # 使用class组合定位包含"主页"文本的元素
            main_page_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(@class, 'x1lliihq') and contains(@class, 'x193iq5w') and contains(@class, 'x6ikm8r') and contains(text(), '主页')]")
                )
            )
            if main_page_element:
                print("[登录服务] 通过主页元素验证登录成功")
                return True
        except Exception:
            print("[登录服务] 主页元素验证失败")
        
            
        # 如果所有明确的验证方法都失败，等待一段时间后再次检查URL
        time.sleep(5)
        new_url = driver.current_url
        if "logged_in" in new_url or "explore" in new_url:
            print(f"[登录服务] 延迟后通过URL验证登录成功: {new_url}")
            return True
        
        print(f"[登录服务] 所有验证方法都失败，当前URL: {new_url}")
        return False


# 如果直接运行此文件，则进行简单的登录测试
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    # 创建Chrome浏览器实例
    options = Options()
    options.add_argument("--start-maximized")
    
    # ✅ 设置固定的用户数据目录 
    options.add_argument(r"--user-data-dir=C:\Users\hou\AppData\Local\Google\selenium_profile") 
    
    # ✅ 可选：给它取个独立的 profile 名称（避免与系统 Chrome 冲突） 
    options.add_argument(r"--profile-directory=Default")
    
    try:
        # 使用webdriver-manager自动管理ChromeDriver
        print("[测试] 正在初始化浏览器...")
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"[测试] 自动下载ChromeDriver失败: {e}")
            print("[测试] 尝试使用系统已安装的ChromeDriver...")
            # 尝试不指定service，让Selenium自动查找系统PATH中的ChromeDriver
            driver = webdriver.Chrome(options=options)
        
        # 创建登录服务实例并尝试登录
        login_service = InstagramLoginService()
        login_service.login(driver)
        
        # 保持浏览器打开一段时间以便观察
        print("[测试] 浏览器将保持打开30秒...")
        time.sleep(30)
        
    finally:
        # 关闭浏览器
        print("[测试] 关闭浏览器")
        driver.quit()