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
        填充帖子描述文本框 - 支持contenteditable div和textarea
        
        Args:
            text_content: 要填充的文本内容
            
        Returns:
            bool: 填充是否成功
        """
        try:
            print("[文本处理服务] 查找描述文本框...")
            
            # 基于实际页面结构优化的定位策略
            caption_locators = [
                # 通过你提供的实际元素属性定位 - contenteditable div
                (By.XPATH, "//div[@aria-label='输入说明文字...' and @contenteditable='true']"),
                (By.XPATH, "//div[@aria-label='输入说明文字...' and @role='textbox']"),
                # 通过data-lexical-editor属性定位
                (By.XPATH, "//div[@data-lexical-editor='true' and @contenteditable='true']"),
                # 通过aria-placeholder定位
                (By.XPATH, "//div[@aria-placeholder='输入说明文字...' and @contenteditable='true']"),
                # CSS选择器定位
                (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='说明']"),
                (By.CSS_SELECTOR, "div[data-lexical-editor='true']"),
            ]
            
            text_element = None
            element_type = None
            
            for i, (by, value) in enumerate(caption_locators):
                try:
                    print(f"[文本处理服务] 尝试定位策略 {i+1}: {by}={value}")
                    text_element = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    
                    # 判断元素类型
                    tag_name = text_element.tag_name.lower()
                    if tag_name == 'div' and text_element.get_attribute('contenteditable') == 'true':
                        element_type = 'contenteditable_div'
                        print("[文本处理服务] 成功找到contenteditable描述文本框")
                    elif tag_name == 'textarea':
                        element_type = 'textarea'
                        print("[文本处理服务] 成功找到textarea描述文本框")
                    else:
                        element_type = 'other'
                        print(f"[文本处理服务] 成功找到描述文本框（类型: {tag_name}）")
                    break
                    
                except Exception as e:
                    print(f"[文本处理服务] 定位策略 {i+1} 失败: {e}")
            
            if text_element:
                # 根据元素类型采用不同的输入方式
                if element_type == 'contenteditable_div':
                    print("[文本处理服务] 使用contenteditable div方式输入文本")
                    return self._fill_contenteditable_div(text_element, text_content)
                elif element_type == 'textarea':
                    print("[文本处理服务] 使用textarea方式输入文本")
                    return self._fill_textarea(text_element, text_content)
                else:
                    print(f"[文本处理服务] 使用通用方式输入文本（类型: {element_type}）")
                    return self._fill_generic_element(text_element, text_content)
                    
            else:
                print("[文本处理服务] 无法找到描述文本框，所有定位策略均失败")
                return False
                
        except Exception as e:
            print(f"[文本处理服务] 填充描述文本时出错: {e}")
            return False
    
    def _fill_contenteditable_div(self, element, text):
        """
        在 Instagram (Lexical) 输入框中稳定输入文本
        """

        try:
            element.click()
            time.sleep(0.2)

            # 清空（适配 IG）
            element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.1)
            element.send_keys(Keys.DELETE)
            time.sleep(0.1)

            # 逐字输入（最稳定的方式）
            for ch in text:
                # 使用 WebDriver 原生 send_keys 模拟真实输入
                element.send_keys(ch)
                time.sleep(0.1)  # IG 反作弊：必须稍微间隔

            # 可选：最后加个空格触发 IG 内部的更新
            element.send_keys(" ")
            time.sleep(4)

            # 验证
            final = element.get_attribute("innerText").strip()
            return text.strip() in final

        except Exception as e:
            print("填充失败：", e)
            return False

    
    def _fill_textarea(self, element, text_content):
        """
        填充textarea元素
        
        Args:
            element: textarea元素
            text_content: 要填充的文本内容
            
        Returns:
            bool: 填充是否成功
        """
        try:
            print("[文本处理服务] 清空textarea内容")
            
            # 清空现有内容
            element.clear()
            
            print("[文本处理服务] 开始输入文本到textarea")
            
            # 分段输入文本
            chunks = self._split_text_to_chunks(text_content)
            
            for i, chunk in enumerate(chunks):
                print(f"[文本处理服务] 输入文本块 {i+1}/{len(chunks)} 到textarea")
                element.send_keys(chunk)
                time.sleep(0.1)
            
            # 触发事件
            element.send_keys(Keys.TAB)
            time.sleep(0.5)
            
            print("[文本处理服务] textarea文本填充完成")
            return True
            
        except Exception as e:
            print(f"[文本处理服务] textarea填充失败: {e}")
            return False
    
    def _fill_generic_element(self, element, text_content):
        """
        通用元素填充方法
        
        Args:
            element: 任意可输入元素
            text_content: 要填充的文本内容
            
        Returns:
            bool: 填充是否成功
        """
        try:
            print(f"[文本处理服务] 使用通用方法输入文本到{element.tag_name}元素")
            
            # 尝试清空内容
            try:
                element.clear()
            except:
                pass
            
            # 分段输入文本
            chunks = self._split_text_to_chunks(text_content)
            
            for i, chunk in enumerate(chunks):
                print(f"[文本处理服务] 输入文本块 {i+1}/{len(chunks)}")
                
                try:
                    element.send_keys(chunk)
                except Exception:
                    # 如果send_keys失败，尝试JavaScript
                    self.driver.execute_script("arguments[0].value += arguments[1];", element, chunk)
                
                time.sleep(0.1)
            
            print("[文本处理服务] 通用元素文本填充完成")
            return True
            
        except Exception as e:
            print(f"[文本处理服务] 通用元素填充失败: {e}")
            return False
    
    def _split_text_to_chunks(self, text, max_chunk_size=50):
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
    
    def wait_for_textarea_ready(self, timeout=15):
        """
        等待文本框准备就绪 - 支持contenteditable div和textarea
        
        Args:
            timeout: 等待超时时间（秒）
            
        Returns:
            bool: 文本框是否就绪
        """
        try:
            print("[文本处理服务] 等待文本框准备就绪...")
            
            # 检查contenteditable div是否可交互（基于你提供的实际元素）
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return ("
                    "document.querySelector('div[contenteditable=\\\"true\\\"][aria-label*=\\\"说明\\\"]') !== null && "
                    "document.querySelector('div[contenteditable=\\\"true\\\"][aria-label*=\\\"说明\\\"]').checkVisibility()"
                    ") || ("
                    
                    "document.querySelector('div[contenteditable=\\\"true\\\"][aria-label*=\\\"输入说明文字\\\"]') !== null && "
                    "document.querySelector('div[contenteditable=\\\"true\\\"][aria-label*=\\\"输入说明文字\\\"]').checkVisibility()"
                    ") || ("
                    
                    "document.querySelector('div[data-lexical-editor=\\\"true\\\"]') !== null && "
                    "document.querySelector('div[data-lexical-editor=\\\"true\\\"]').checkVisibility()"
                    ") || ("
                    
                    "document.querySelector('textarea[aria-label*=\\\"说明\\\"]') !== null && "
                    "document.querySelector('textarea[aria-label*=\\\"说明\\\"]').checkVisibility()"
                    ") || ("
                    
                    "document.querySelector('textarea[aria-label*=\\\"caption\\\"]') !== null && "
                    "document.querySelector('textarea[aria-label*=\\\"caption\\\"]').checkVisibility()"
                    ")"
                )
            )
            
            print("[文本处理服务] 文本框准备就绪")
            return True
        except Exception as e:
            print(f"[文本处理服务] 文本框未准备就绪: {e}")
            return False
    
    def check_text_content(self, expected_content):
        """
        检查文本框内容是否符合预期 - 支持contenteditable div和textarea
        
        Args:
            expected_content: 预期的文本内容
            
        Returns:
            bool: 内容是否符合预期
        """
        try:
            print("[文本处理服务] 检查文本内容...")
            
            # 查找文本框并获取内容 - 支持多种元素类型
            text_element = None
            actual_content = ""
            
            # 尝试定位contenteditable div（基于你提供的实际元素）
            try:
                text_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@aria-label='输入说明文字...' and @contenteditable='true']")
                    )
                )
                # 获取contenteditable div的文本内容
                actual_content = text_element.text or text_element.get_attribute('textContent') or ""
                print("[文本处理服务] 从contenteditable div获取内容")
            except:
                try:
                    text_element = self.driver.find_element(
                        By.XPATH, "//div[@data-lexical-editor='true' and @contenteditable='true']"
                    )
                    actual_content = text_element.text or text_element.get_attribute('textContent') or ""
                    print("[文本处理服务] 从data-lexical-editor div获取内容")
                except:
                    # 尝试传统的textarea
                    try:
                        text_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//textarea[@aria-label='添加说明，标记人物...']")
                            )
                        )
                        actual_content = text_element.get_attribute('value') or ""
                        print("[文本处理服务] 从textarea获取内容")
                    except:
                        try:
                            text_element = self.driver.find_element(
                                By.XPATH, "//textarea[@aria-label='Write a caption...']"
                            )
                            actual_content = text_element.get_attribute('value') or ""
                            print("[文本处理服务] 从英文textarea获取内容")
                        except:
                            pass
            
            if text_element and actual_content:
                # 清理内容进行比较（去除多余空白字符）
                actual_clean = ' '.join(actual_content.split())
                expected_clean = ' '.join(expected_content.split())
                
                print(f"[文本处理服务] 实际内容长度: {len(actual_content)} 字符")
                print(f"[文本处理服务] 预期内容长度: {len(expected_content)} 字符")
                
                # 检查预期内容是否在实际内容中
                if expected_clean in actual_clean:
                    print("[文本处理服务] 文本内容检查通过")
                    return True
                else:
                    print(f"[文本处理服务] 文本内容不匹配")
                    print(f"预期包含: {expected_clean[:50]}...")
                    print(f"实际内容: {actual_clean[:50]}...")
                    return False
            else:
                print("[文本处理服务] 无法找到文本框或获取内容进行内容检查")
                return False
        except Exception as e:
            print(f"[文本处理服务] 检查文本内容时出错: {e}")
            return False
    
    def clear_textarea(self):
        """
        清空文本框内容 - 支持contenteditable div和textarea
        """
        try:
            print("[文本处理服务] 清空文本框...")
            
            # 查找文本框 - 支持contenteditable div和textarea
            text_element = None
            
            # 尝试定位contenteditable div（基于你提供的实际元素）
            try:
                text_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@aria-label='输入说明文字...' and @contenteditable='true']")
                    )
                )
                print("[文本处理服务] 找到contenteditable div进行清空")
            except:
                try:
                    text_element = self.driver.find_element(
                        By.XPATH, "//div[@data-lexical-editor='true' and @contenteditable='true']"
                    )
                    print("[文本处理服务] 找到data-lexical-editor div进行清空")
                except:
                    # 尝试传统的textarea
                    try:
                        text_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//textarea[@aria-label='添加说明，标记人物...']")
                            )
                        )
                        print("[文本处理服务] 找到textarea进行清空")
                    except:
                        try:
                            text_element = self.driver.find_element(
                                By.XPATH, "//textarea[@aria-label='Write a caption...']"
                            )
                            print("[文本处理服务] 找到英文textarea进行清空")
                        except:
                            pass
            
            if text_element:
                # 根据元素类型选择清空方法
                if text_element.tag_name.lower() == 'div' and text_element.get_attribute('contenteditable') == 'true':
                    # 处理contenteditable div
                    self.driver.execute_script("arguments[0].innerHTML = '<p><br></p>';", text_element)
                    print("[文本处理服务] 使用JavaScript清空contenteditable div")
                else:
                    # 处理textarea
                    try:
                        text_element.clear()
                    except:
                        pass
                    
                    # 确保清空（有时需要额外操作）
                    text_element.send_keys(Keys.CONTROL + "a")
                    text_element.send_keys(Keys.DELETE)
                    print("[文本处理服务] 使用键盘操作清空textarea")
                
                print("[文本处理服务] 文本框已清空")
                return True
            else:
                print("[文本处理服务] 无法找到文本框进行清空")
                return False
            
        except Exception as e:
            print(f"[文本处理服务] 清空文本框失败: {e}")
            return False
    
    def get_textarea_content(self):
        """
        获取文本框内容 - 支持contenteditable div和textarea
        
        Returns:
            str: 文本框内容，如果获取失败返回空字符串
        """
        try:
            print("[文本处理服务] 获取文本框内容...")
            
            # 查找文本框并获取内容 - 支持多种元素类型
            text_element = None
            actual_content = ""
            
            # 尝试定位contenteditable div（基于你提供的实际元素）
            try:
                text_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@aria-label='输入说明文字...' and @contenteditable='true']")
                    )
                )
                # 获取contenteditable div的文本内容
                actual_content = text_element.text or text_element.get_attribute('textContent') or ""
                print(f"[文本处理服务] 从contenteditable div获取内容: {len(actual_content)} 字符")
            except:
                try:
                    text_element = self.driver.find_element(
                        By.XPATH, "//div[@data-lexical-editor='true' and @contenteditable='true']"
                    )
                    actual_content = text_element.text or text_element.get_attribute('textContent') or ""
                    print(f"[文本处理服务] 从data-lexical-editor div获取内容: {len(actual_content)} 字符")
                except:
                    # 尝试传统的textarea
                    try:
                        text_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//textarea[@aria-label='添加说明，标记人物...']")
                            )
                        )
                        actual_content = text_element.get_attribute('value') or ""
                        print(f"[文本处理服务] 从textarea获取内容: {len(actual_content)} 字符")
                    except:
                        try:
                            text_element = self.driver.find_element(
                                By.XPATH, "//textarea[@aria-label='Write a caption...']"
                            )
                            actual_content = text_element.get_attribute('value') or ""
                            print(f"[文本处理服务] 从英文textarea获取内容: {len(actual_content)} 字符")
                        except:
                            pass
            
            if text_element and actual_content:
                # 清理内容（去除多余空白字符）
                actual_clean = ' '.join(actual_content.split())
                print(f"[文本处理服务] 获取到的内容: {actual_clean[:100]}...")
                return actual_clean
            else:
                print("[文本处理服务] 无法找到文本框或获取内容")
                return ""
                
        except Exception as e:
            print(f"[文本处理服务] 获取文本框内容时出错: {e}")
            return ""