from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# 导入服务模块
from service.login import InstagramLoginService
from service.post_service import InstagramPostService

def read_file_content(file_path):
    """
    读取指定txt文件的内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件内容，如果文件不存在则返回空字符串
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                print(f"[文件操作] 成功读取文件: {file_path}, 内容长度: {len(content)} 字符")
                return content
        else:
            print(f"[文件操作] 警告: 文件不存在: {file_path}")
            return ""
    except Exception as e:
        print(f"[文件操作] 读取文件时出错: {e}")
        return ""

def fill_input_box(driver, text_content):
    """
    查找Instagram帖子描述输入框并填入内容
    
    Args:
        driver: Selenium WebDriver实例
        text_content: 要填入输入框的内容
        
    Returns:
        bool: 操作是否成功
    """
    try:
        print("[输入框操作] 正在查找帖子描述输入框...")
        
        # 尝试多种定位策略查找输入框
        input_locators = [
            # 定位策略2: 通过aria-label定位
            (By.XPATH, "//textarea[@aria-label]"),
            # 定位策略3: 通过class名称定位
            (By.XPATH, "//div[@role='textbox']"),
            # 定位策略4: 通过name属性定位
            (By.NAME, "caption"),
        ]
        
        input_element = None
        for i, (by, value) in enumerate(input_locators):
            try:
                print(f"[输入框操作] 尝试定位策略 {i+1}: {by}={value}")
                input_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by, value))
                )
                print(f"[输入框操作] 成功找到输入框")
                break
            except Exception as e:
                print(f"[输入框操作] 定位策略 {i+1} 失败: {e}")
        
        if input_element:
            # 清空输入框并填入内容
            input_element.clear()
            # 由于内容可能较长，分块输入
            chunks = [text_content[i:i+100] for i in range(0, len(text_content), 100)]
            for chunk in chunks:
                input_element.send_keys(chunk)
                time.sleep(0.1)  # 短暂停顿避免过快输入
            
            print(f"[输入框操作] 成功将内容填入输入框，内容长度: {len(text_content)} 字符")
            return True
        else:
            print("[输入框操作] 无法找到输入框")
            return False
    except Exception as e:
        print(f"[输入框操作] 操作输入框时出错: {e}")
        return False

def test_instagram_upload():
    """
    测试Instagram登录、创建帖子和上传1.jpg的完整流程
    """
    driver = None
    try:
        # 1. 初始化浏览器
        print("[测试] 正在初始化浏览器...")
        options = Options()
        options.add_argument("--start-maximized")
        # ✅ 设置固定的用户数据目录
        options.add_argument(r"--user-data-dir=C:\Users\hou\AppData\Local\Google\selenium_profile")
        # ✅ 可选：给它取个独立的 profile 名称（避免与系统 Chrome 冲突）
        options.add_argument(r"--profile-directory=Default")
        
        # 使用webdriver-manager自动管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 2. 登录Instagram
        print("\n[测试] 开始登录Instagram...")
        login_service = InstagramLoginService()
        login_success = login_service.login(driver)
        
        if not login_success:
            print("[测试] 登录失败，退出测试")
            return False
        
        # 等待页面完全加载
        print("[测试] 登录成功，等待页面完全加载...")
        time.sleep(5)
        
        # 3. 初始化发布服务
        post_service = InstagramPostService(driver)
        
        # 4. 点击创建帖子按钮
        print("\n[测试] 尝试点击创建帖子按钮...")
        create_success = post_service.click_create_post_button()
        
        if not create_success:
            print("[测试] 点击创建按钮失败，退出测试")
            return False
        
        # 5. 等待上传界面加载
        print("[测试] 创建按钮点击成功，等待上传界面...")
        upload_interface_ready = post_service.wait_for_upload_interface()
        
        if not upload_interface_ready:
            print("[测试警告] 上传界面检测失败，但将继续尝试上传")
        
        # 6. 上传1.jpg文件
        print("\n[测试] 尝试上传1.jpg文件...")
        # 获取1.jpg的绝对路径
        file_path = os.path.abspath("1.jpg")
        print(f"[测试] 上传文件路径: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"[测试] 错误: 文件 {file_path} 不存在")
            return False
        
        upload_success = post_service.upload_media(file_path)
        
        if upload_success:
            print("[测试] 文件上传成功！")
            # 点击下一步按钮
            print("[测试] 点击下一步按钮...")
            post_service.go_to_next_step()

            # 点击下一步按钮
            print("\n[测试] 继续点击下一步按钮...")
            post_service.go_to_next_step()

            # 读取1.txt文件内容
            print("\n[测试] 开始处理文本内容...")
            file_content = read_file_content("1.txt")
            
            if file_content:
                # 将文件内容填入输入框
                print("[测试] 正在将文件内容填入输入框...")
                fill_input_box(driver, file_content)
            else:
                print("[测试] 未获取到文件内容，跳过输入框填充")
            
            # 保持浏览器打开一段时间以便观察
            print("\n[测试] 测试完成！浏览器将保持打开60秒，您可以观察结果...")
            time.sleep(60)
            return True
        else:
            print("[测试] 文件上传失败")
            return False
            
    except Exception as e:
        print(f"[测试] 发生错误: {e}")
        return False
    finally:
        # 关闭浏览器
        if driver:
            print("[测试] 关闭浏览器")
            driver.quit()

if __name__ == "__main__":
    print("=== Instagram上传测试开始 ===")
    success = test_instagram_upload()
    
    if success:
        print("=== 测试成功 ===")
    else:
        print("=== 测试失败 ===")