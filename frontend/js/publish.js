document.addEventListener('DOMContentLoaded', function() {
    // 图片选择相关元素
    const weekdaySelect = document.getElementById('weekday-select');
    const imageSelect = document.getElementById('image-select');
    const selectedImageInfo = document.getElementById('selected-image-info');
    const selectedImagePath = document.getElementById('selected-image-path');
    const removeSelectedImageBtn = document.getElementById('remove-selected-image');
    const postCaption = document.getElementById('post-caption');
    const charCount = document.getElementById('char-count');
    const publishBtn = document.getElementById('publish-btn');
    const publishStatus = document.getElementById('publish-status');


    let selectedFile = null;

    // 页面加载时获取今日内容
    loadTodayContent();

    // 文案字数统计
    postCaption.addEventListener('input', function() {
        const length = this.value.length;
        charCount.textContent = length;
        
        if (length > 2000) {
            charCount.parentElement.classList.add('danger');
            charCount.parentElement.classList.remove('warning');
        } else if (length > 1800) {
            charCount.parentElement.classList.add('warning');
            charCount.parentElement.classList.remove('danger');
        } else {
            charCount.parentElement.classList.remove('warning', 'danger');
        }
    });



    // 获取今日内容函数（已废弃）
    async function loadTodayContent() {
        // 此功能已废弃，不再自动加载今日内容
    }

    // 显示通知函数
    function showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // 添加样式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-size: 14px;
            z-index: 1000;
            transition: all 0.3s ease;
            transform: translateX(100%);
            opacity: 0;
        `;
        
        // 根据类型设置背景色
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 100);
        
        // 自动隐藏
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // 发布功能
    publishBtn.addEventListener('click', function() {
        if (!selectedFile) {
            showNotification('请先选择要发布的图片！', 'error');
            return;
        }

        if (postCaption.value.trim().length === 0) {
            showNotification('请输入帖子文案！', 'error');
            return;
        }

        publishPost();
    });

    async function publishPost() {
        publishBtn.disabled = true;
        publishBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发布中...';

        try {
            // 由于我们选择的是服务器上的文件，需要修改发布逻辑
            const formData = new FormData();
            formData.append('image_path', selectedFile.path); // 使用文件路径而不是文件对象
            formData.append('content', postCaption.value);

            const response = await fetch('http://localhost:5000/api/publish', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('发布成功！', 'success');
                // 重置表单
                selectedFile = null;
                postCaption.value = '';
                charCount.textContent = '0';
                
                // 隐藏已选图片信息
                selectedImageInfo.style.display = 'none';
                
                // 重置图片选择
                imageSelect.value = '';
                weekdaySelect.value = '';
                
            } else {
                showNotification('发布失败：' + data.message, 'error');
            }
        } catch (error) {
            console.error('发布失败:', error);
            showNotification('发布失败，请检查网络连接', 'error');
        } finally {
            publishBtn.disabled = false;
            publishBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发布到Instagram';
        }
    }

    function showStatus(message, type) {
        publishStatus.textContent = message;
        publishStatus.className = `publish-status ${type}`;
        publishStatus.style.display = 'block';
        
        setTimeout(() => {
            publishStatus.style.display = 'none';
        }, 5000);
    }

    // 星期选择变化事件
    weekdaySelect.addEventListener('change', function() {
        const selectedWeekday = this.value;
        imageSelect.innerHTML = '<option value="">加载中...</option>';
        
        if (selectedWeekday) {
            loadImagesForWeekday(selectedWeekday);
        } else {
            imageSelect.innerHTML = '<option value="">请先选择图片</option>';
            imageSelect.disabled = true;
            selectedImageInfo.style.display = 'none';
        }
    });
    
    // 图片选择变化事件
    imageSelect.addEventListener('change', function() {
        const selectedImage = this.value;
        
        if (selectedImage) {
            const fullPath = `d:/otherWorkspace/ins-robot/data/media/${weekdaySelect.value}/${selectedImage}`;
            selectedImagePath.textContent = fullPath;
            selectedImageInfo.style.display = 'block';
            
            // 模拟文件对象
            selectedFile = {
                name: selectedImage,
                size: 1024 * 1024, // 假设1MB
                path: fullPath
            };
            
            // 根据图片文件名加载对应的文案
            loadTextContentForImage(selectedImage, weekdaySelect.value);
        } else {
            selectedImageInfo.style.display = 'none';
            selectedFile = null;
            // 清空文案
            postCaption.value = '';
            charCount.textContent = '0';
        }
    });
    
    // 根据图片文件名加载对应的文案
    async function loadTextContentForImage(imageFilename, weekday) {
        try {
            // 获取不带扩展名的文件名（处理文件名中包含多个点的情况，如2.55.jpg）
            const lastDotIndex = imageFilename.lastIndexOf('.');
            const baseName = lastDotIndex !== -1 ? imageFilename.substring(0, lastDotIndex) : imageFilename;
            const textFilename = `${baseName}.txt`;
            const textPath = `d:/otherWorkspace/ins-robot/data/media/${weekday}/${textFilename}`;
            
            console.log(`尝试加载文案文件: ${textPath}`);
            
            // 尝试读取对应的txt文件
            const response = await fetch(`http://localhost:5000/api/text-content/${weekday}/${textFilename}`);
            
            if (response.ok) {
                const result = await response.json();
                if (result.success && result.data && result.data.content) {
                    postCaption.value = result.data.content;
                    // 手动触发input事件来更新字符计数
                    const event = new Event('input');
                    postCaption.dispatchEvent(event);
                    showNotification(`已自动加载对应文案: ${textFilename}`, 'success');
                } else {
                    showNotification(`文案文件为空: ${textFilename}`, 'warning');
                }
            } else {
                console.log(`未找到对应的文案文件: ${textFilename}`);
                showNotification(`未找到对应文案: ${textFilename}`, 'info');
                // 清空文案框
                postCaption.value = '';
                charCount.textContent = '0';
            }
        } catch (error) {
            console.error('加载文案失败:', error);
            showNotification('加载对应文案失败', 'error');
            // 清空文案框
            postCaption.value = '';
            charCount.textContent = '0';
        }
    }
    
    // 移除图片按钮事件
    removeSelectedImageBtn.addEventListener('click', function() {
        weekdaySelect.value = '';
        imageSelect.innerHTML = '<option value="">请先选择星期</option>';
        imageSelect.disabled = true;
        selectedImageInfo.style.display = 'none';
        selectedFile = null;
    });
    
    // 加载指定星期的图片列表
    async function loadImagesForWeekday(weekday) {
        try {
            const response = await fetch(`http://localhost:5000/api/weekday-images/${weekday}`);
            const result = await response.json();
            
            if (result.success) {
                const images = result.data.images;
                
                if (images.length > 0) {
                    imageSelect.innerHTML = '<option value="">请选择图片</option>';
                    images.forEach(image => {
                        const option = document.createElement('option');
                        option.value = image.filename;
                        option.textContent = `${image.filename} (${image.size_mb}MB)`;
                        imageSelect.appendChild(option);
                    });
                    imageSelect.disabled = false;
                } else {
                    imageSelect.innerHTML = '<option value="">该星期暂无图片</option>';
                    imageSelect.disabled = true;
                }
            } else {
                imageSelect.innerHTML = '<option value="">加载失败</option>';
                imageSelect.disabled = true;
                showNotification(`加载图片列表失败: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('加载图片列表出错:', error);
            imageSelect.innerHTML = '<option value="">加载出错</option>';
            imageSelect.disabled = true;
            showNotification('加载图片列表出错，请检查网络连接', 'error');
        }
    }
});