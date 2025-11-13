from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re

class TextProcessingService:
    """
    文本处理服务类，提供Instagram文本处理相关功能
    """
    
    def __init__(self, driver):
        """
        初始化文本处理服务
        
        Args:
            driver: Selenium WebDriver实例
        """
        self.driver = driver
    
    def fill_caption_textarea(self, text_content):
        """
        填充帖子描述文本框
        
        Args:
            text_content: 要填充的文本内容
            
        Returns:
            bool: 填充是否成功
        """
        try:
            print("[文本处理服务] 查找描述文本框...")
            
            # 尝试多种定位策略
            caption_locators = [
                # 通过aria-label定位
                (By.XPATH, "//textarea[@aria-label='添加说明，标记人物...']"),
                (By.XPATH, "//textarea[@aria-label='Write a caption...']"),
                # 通过class定位
                (By.XPATH, "//div[contains(@class, '_ac7b') and contains(@class, '_ac7c')]//textarea")
            ]
            
            textarea = None
            for i, (by, value) in enumerate(caption_locators):
                try:
                    print(f"[文本处理服务] 尝试定位策略 {i+1}: {by}={value}")
                    textarea = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    print("[文本处理服务] 成功找到描述文本框")
                    break
                except Exception as e:
                    print(f"[文本处理服务] 定位策略 {i+1} 失败: {e}")
            
            if textarea:
                # 清除可能存在的文本
                textarea.clear()
                
                # 分段输入文本，避免一次性输入过多导致问题
                chunks = self._split_text_to_chunks(text_content)
                
                for i, chunk in enumerate(chunks):
                    print(f"[文本处理服务] 输入文本块 {i+1}/{len(chunks)}")
                    textarea.send_keys(chunk)
                    # 短暂停顿，确保输入稳定
                    time.sleep(0.1)
                
                # 等待文本完全加载
                time.sleep(1)
                print("[文本处理服务] 描述文本填充完成")
                return True
            else:
                print("[文本处理服务] 无法找到描述文本框")
                return False
        except Exception as e:
            print(f"[文本处理服务] 填充描述文本时出错: {e}")
            return False
    
    def _split_text_to_chunks(self, text, max_chunk_size=100):
        """
        将长文本分割成多个小块
        
        Args:
            text: 原始文本
            max_chunk_size: 每个块的最大大小
            
        Returns:
            list: 文本块列表
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        i = 0
        while i < len(text):
            # 尝试在空格处分割，避免截断单词
            end = min(i + max_chunk_size, len(text))
            if end < len(text):
                # 寻找最后的空格或标点符号
                while end > i and text[end] not in (' ', '\n', '!', '.', ',', ';', ':', '?'):
                    end -= 1
                
                # 如果找不到合适的分割点，就直接在最大长度处分割
                if end == i:
                    end = i + max_chunk_size
            
            chunks.append(text[i:end])
            i = end
        
        return chunks
    
    def process_hashtags(self, text_content):
        """
        处理文本中的标签，确保格式正确
        
        Args:
            text_content: 包含标签的文本内容
            
        Returns:
            str: 处理后的文本内容
        """
        try:
            # 确保标签格式正确
            # 这里可以添加更多的标签处理逻辑，比如标签去重、标签数量限制等
            print("[文本处理服务] 处理文本中的标签")
            
            # 简单的标签格式验证（可选）
            hashtags = re.findall(r'#\w+', text_content)
            print(f"[文本处理服务] 识别到 {len(hashtags)} 个标签")
            
            return text_content
        except Exception as e:
            print(f"[文本处理服务] 处理标签时出错: {e}")
            return text_content
    
    def wait_for_textarea_ready(self, timeout=10):
        """
        等待文本框准备就绪
        
        Args:
            timeout: 等待超时时间（秒）
            
        Returns:
            bool: 文本框是否就绪
        """
        try:
            print("[文本处理服务] 等待文本框准备就绪...")
            
            # 检查文本框是否可交互
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return document.querySelector('textarea[aria-label*=\"说明\"], textarea[aria-label*=\"caption\"]') !== null && "
                    "document.querySelector('textarea[aria-label*=\"说明\"], textarea[aria-label*=\"caption\"]').checkVisibility()"
                )
            )
            
            print("[文本处理服务] 文本框准备就绪")
            return True
        except Exception as e:
            print(f"[文本处理服务] 文本框未准备就绪: {e}")
            return False
    
    def check_text_content(self, expected_content):
        """
        检查文本框内容是否符合预期
        
        Args:
            expected_content: 预期的文本内容
            
        Returns:
            bool: 内容是否符合预期
        """
        try:
            print("[文本处理服务] 检查文本内容...")
            
            # 查找文本框并获取内容
            textarea = None
            try:
                textarea = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//textarea[@aria-label='添加说明，标记人物...']")
                    )
                )
            except:
                try:
                    textarea = self.driver.find_element(
                        By.XPATH, "//textarea[@aria-label='Write a caption...']"
                    )
                except:
                    pass
            
            if textarea:
                actual_content = textarea.get_attribute('value')
                
                # 简单的内容匹配检查
                # 这里可以根据需要调整匹配策略
                if expected_content in actual_content:
                    print("[文本处理服务] 文本内容检查通过")
                    return True
                else:
                    print(f"[文本处理服务] 文本内容不匹配: 预期包含 '{expected_content}'，实际内容长度: {len(actual_content)} 字符")
                    return False
            else:
                print("[文本处理服务] 无法找到文本框进行内容检查")
                return False
        except Exception as e:
            print(f"[文本处理服务] 检查文本内容时出错: {e}")
            return False