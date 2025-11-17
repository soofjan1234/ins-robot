document.addEventListener('DOMContentLoaded', function() {
    const imageUploadArea = document.getElementById('image-upload-area');
    const imageInput = document.getElementById('image-input');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const removeImageBtn = document.getElementById('remove-image');
    const selectImageBtn = document.getElementById('select-image-btn');
    const imageInfo = document.getElementById('image-info');
    const postCaption = document.getElementById('post-caption');
    const charCount = document.getElementById('char-count');
    const publishBtn = document.getElementById('publish-btn');
    const publishStatus = document.getElementById('publish-status');


    let selectedFile = null;

    // 页面加载时获取今日内容
    loadTodayContent();

    // 图片上传功能
    imageUploadArea.addEventListener('click', function() {
        if (!selectedFile) {
            imageInput.click();
        }
    });

    selectImageBtn.addEventListener('click', function() {
        imageInput.click();
    });

    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleImageUpload(file);
        }
    });

    // 拖拽上传
    imageUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#667eea';
        imageUploadArea.style.backgroundColor = '#f0f4ff';
    });

    imageUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#ddd';
        imageUploadArea.style.backgroundColor = '#fafafa';
    });

    imageUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#ddd';
        imageUploadArea.style.backgroundColor = '#fafafa';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                handleImageUpload(file);
            } else {
                showStatus('请上传图片文件！', 'error');
            }
        }
    });

    function handleImageUpload(file) {
        if (!file.type.startsWith('image/')) {
            showStatus('请上传有效的图片文件！', 'error');
            return;
        }

        selectedFile = file;
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            uploadPlaceholder.style.display = 'none';
            imagePreview.style.display = 'block';
            imageUploadArea.classList.add('has-image');
            
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            imageInfo.textContent = `${file.name} (${fileSize}MB)`;
        };
        
        reader.readAsDataURL(file);
    }

    // 移除图片
    removeImageBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        selectedFile = null;
        imageInput.value = '';
        uploadPlaceholder.style.display = 'flex';
        imagePreview.style.display = 'none';
        imageUploadArea.classList.remove('has-image');
        imageInfo.textContent = '未选择图片';
    });

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



    // 获取今日内容函数
    async function loadTodayContent() {
        try {
            const response = await fetch('http://localhost:5000/api/today-content');
            const result = await response.json();
            
            if (result.success) {
                console.log('今日内容加载成功:', result.data);
                
                // 如果有文本内容，自动填充到文案框
                if (result.data.texts && result.data.texts.length > 0) {
                    const firstText = result.data.texts[0];
                    postCaption.value = firstText.content;
                    // 手动触发input事件来更新字符计数
                    const event = new Event('input');
                    postCaption.dispatchEvent(event);
                    showNotification(`已加载今日${result.data.today}的文案内容`, 'success');
                }
                
            } else {
                console.warn('获取今日内容失败:', result.message);
                showNotification('暂无今日内容，请手动上传', 'info');
            }
        } catch (error) {
            console.error('加载今日内容出错:', error);
            showNotification('加载今日内容失败，请手动操作', 'error');
        }
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
            showStatus('请先选择要发布的图片！', 'error');
            return;
        }

        if (postCaption.value.trim().length === 0) {
            showStatus('请输入帖子文案！', 'error');
            return;
        }

        publishPost();
    });

    function publishPost() {
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('content', postCaption.value);

        publishBtn.disabled = true;
        publishBtn.innerHTML = '<span class="btn-icon">⏳</span> 发布中...';
        showStatus('正在发布帖子...', 'info');

        // 模拟API调用
        setTimeout(() => {
            showStatus('帖子发布成功！', 'success');
            publishBtn.disabled = false;
            publishBtn.innerHTML = '<span class="btn-icon">📤</span> 立即发布';
            
            // 3秒后跳转到首页
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 3000);
        }, 2000);

        /* 实际API调用代码（需要后端支持）
        fetch('/api/publish', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('帖子发布成功！', 'success');
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
            } else {
                showStatus('发布失败：' + data.message, 'error');
            }
        })
        .catch(error => {
            showStatus('发布失败：' + error.message, 'error');
        })
        .finally(() => {
            publishBtn.disabled = false;
            publishBtn.innerHTML = '<span class="btn-icon">📤</span> 立即发布';
        });
        */
    }

    function showStatus(message, type) {
        publishStatus.textContent = message;
        publishStatus.className = `publish-status ${type}`;
        publishStatus.style.display = 'block';
        
        setTimeout(() => {
            publishStatus.style.display = 'none';
        }, 5000);
    }

    // 初始化
    imageInfo.textContent = '未选择图片';
});