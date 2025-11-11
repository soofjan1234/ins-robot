from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 导入登录服务
from service.login import InstagramLoginService

# 创建Chrome浏览器实例
options = Options()
# 可以添加其他选项，例如最大化窗口
options.add_argument("--start-maximized")

# 使用webdriver-manager自动管理ChromeDriver
print("正在初始化浏览器...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # 可以选择是否使用登录服务
    use_login = True  # 设置为False则只打开网站不登录
    
    if use_login:
        # 创建登录服务实例
        login_service = InstagramLoginService()
        
        # 可以传入自定义的用户名和密码，或者使用环境变量中的默认值
        # 例如：login_service.login(driver, username="custom_user", password="custom_pass")
        login_success = login_service.login(driver)
        
        if not login_success:
            print("登录失败，将继续使用未登录状态")
    else:
        # 仅打开网站不登录
        print("正在打开Instagram网站（不登录）...")
        driver.get("https://www.instagram.com/")
        time.sleep(5)
    
    # 保持浏览器打开一段时间以便观察
    print("浏览器将保持打开60秒...")
    time.sleep(60)
    
finally:
    # 关闭浏览器
    print("关闭浏览器")
    driver.quit()