/**
 * P图页面JavaScript功能
 * 支持多张图片上传、水印处理和结果展示
 */

class PEditTool {
    constructor() {
        this.uploadedImages = [];
        this.processedImages = [];
        this.watermarkPosition = 'top-right';
        this.watermarkSize = 0.15;
        this.watermarkOpacity = 0.6;
        this.watermarkMargin = 20;
        
        this.initializeEventListeners();
        this.loadPSImages();
    }
    
    /**
     * 从后端加载toPS目录中的图片
     */
    loadPSImages() {
        console.log('正在加载toPS目录中的图片...');
        
        fetch('/api/load-to-ps-imgs')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.data && data.data.images) {
                    console.log(`成功加载 ${data.data.images.length} 张toPS图片`);
                    
                    // 处理加载的图片数据
                    data.data.images.forEach(imageData => {
                        // 创建一个File对象模拟
                        const file = {
                            name: imageData.filename,
                            size: imageData.size,
                            type: this.getMimeTypeFromFilename(imageData.filename)
                        };
                        
                        // 创建一个image对象并添加到上传图片列表
                        const image = {
                            id: Date.now() + Math.random(), // 添加id属性，与addImage方法保持一致
                            file: file,
                            name: imageData.filename,
                            size: this.formatFileSize(imageData.size), // 使用formatFileSize方法格式化大小
                            url: `data:image/${this.getExtensionFromFilename(imageData.filename)};base64,${imageData.data}`,
                            processed: false,
                            filename: imageData.filename
                        };
                        
                        this.uploadedImages.push(image);
                    });
                    
                    // 所有图片添加完成后，渲染预览并更新UI状态
                    if (this.uploadedImages.length > 0) {
                        this.renderPreview();
                        this.showPreviewSection();
                        this.updateUI();
                    }
                } else {
                    console.warn('未加载到toPS图片:', data.message || '未知错误');
                }
            })
            .catch(error => {
                console.error('加载toPS图片失败:', error);
            });
    }
    
    /**
     * 根据文件名获取扩展名
     */
    getExtensionFromFilename(filename) {
        const parts = filename.split('.');
        return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : 'jpg';
    }
    
    /**
     * 根据文件名获取MIME类型
     */
    getMimeTypeFromFilename(filename) {
        const extension = this.getExtensionFromFilename(filename);
        const mimeTypes = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        };
        return mimeTypes[extension] || 'image/jpeg';
    }

    /**
     * 初始化事件监听器
     */
    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const processBtn = document.getElementById('processBtn');
        const clearBtn = document.getElementById('clearBtn');
        const downloadAllBtn = document.getElementById('downloadAllBtn');

        if (uploadArea) {
            // 拖拽上传
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
            uploadArea.addEventListener('drop', this.handleDrop.bind(this));
            // 上传区域点击 - 但排除按钮点击
            uploadArea.addEventListener('click', (e) => {
                // 如果点击的是按钮，不触发文件选择
                if (e.target.classList.contains('upload-btn')) {
                    return;
                }
                fileInput && fileInput.click();
            });
        }

        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }

        // 控制面板
        const watermarkPosition = document.getElementById('watermarkPosition');
        const watermarkSize = document.getElementById('watermarkSize');
        const watermarkOpacity = document.getElementById('watermarkOpacity');
        const watermarkMargin = document.getElementById('watermarkMargin');
        if (watermarkPosition) watermarkPosition.addEventListener('change', this.updateWatermarkSettings.bind(this));
        if (watermarkSize) watermarkSize.addEventListener('input', this.updateWatermarkSettings.bind(this));
        if (watermarkOpacity) watermarkOpacity.addEventListener('input', this.updateWatermarkSettings.bind(this));
        if (watermarkMargin) watermarkMargin.addEventListener('input', this.updateWatermarkSettings.bind(this));

        if (processBtn) processBtn.addEventListener('click', this.startProcessing.bind(this));
        if (clearBtn) clearBtn.addEventListener('click', this.clearAllImages.bind(this));
    }

    /**
     * 处理拖拽悬停
     */
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    /**
     * 处理拖拽离开
     */
    handleDragLeave(e) {
        e.currentTarget.classList.remove('dragover');
    }

    /**
     * 处理文件拖拽
     */
    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files).filter(file => 
            file.type.startsWith('image/')
        );
        
        this.processFiles(files);
    }

    /**
     * 处理文件选择
     */
    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.processFiles(files);
    }

    /**
     * 处理文件列表
     */
    processFiles(files) {
        if (files.length === 0) return;

        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                this.addImage(file);
            }
        });

        this.showPreviewSection();
        this.updateUI();
    }

    /**
     * 添加图片
     */
    addImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                id: Date.now() + Math.random(),
                file: file,
                name: file.name,
                size: this.formatFileSize(file.size),
                url: e.target.result,
                processed: false
            };
            
            this.uploadedImages.push(imageData);
            this.renderPreview();
            this.updateUI();
        };
        reader.readAsDataURL(file);
    }

    /**
     * 渲染预览
     */
    renderPreview() {
        const grid = document.getElementById('imageGrid');
        grid.innerHTML = '';

        this.uploadedImages.forEach(image => {
            const item = document.createElement('div');
            item.className = 'image-item';
            item.innerHTML = `
                <img src="${image.url}" alt="${image.name}">
                <div class="image-item-info">
                    <div>${image.name}</div>
                    <div>${image.size}</div>
                </div>
                <button class="remove-image" onclick="pEditTool.removeImage(${image.id})">×</button>
            `;
            grid.appendChild(item);
        });
    }

    /**
     * 移除图片
     */
    removeImage(id) {
        this.uploadedImages = this.uploadedImages.filter(img => img.id !== id);
        this.renderPreview();
        this.updateUI();
        
        if (this.uploadedImages.length === 0) {
            this.hidePreviewSection();
        }
    }

    /**
     * 显示预览区域
     */
    showPreviewSection() {
        document.getElementById('previewSection').style.display = 'block';
        document.getElementById('controlsSection').style.display = 'block';
        document.getElementById('previewSection').classList.add('fade-in');
        document.getElementById('controlsSection').classList.add('fade-in');
    }

    /**
     * 隐藏预览区域
     */
    hidePreviewSection() {
        document.getElementById('previewSection').style.display = 'none';
        document.getElementById('controlsSection').style.display = 'none';
    }

    /**
     * 更新水印设置
     */
    updateWatermarkSettings() {
        this.watermarkPosition = document.getElementById('watermarkPosition').value;
        this.watermarkSize = parseFloat(document.getElementById('watermarkSize').value);
        this.watermarkOpacity = parseFloat(document.getElementById('watermarkOpacity').value);
        this.watermarkMargin = parseInt(document.getElementById('watermarkMargin').value);

        // 更新显示值
        document.getElementById('sizeValue').textContent = Math.round(this.watermarkSize * 100) + '%';
        document.getElementById('opacityValue').textContent = Math.round(this.watermarkOpacity * 100) + '%';
        document.getElementById('marginValue').textContent = this.watermarkMargin + 'px';
    }

    /**
     * 开始处理图片
     */
    async startProcessing() {
        if (this.uploadedImages.length === 0) {
            alert('请先上传图片！');
            return;
        }

        this.showLoading();
        this.processedImages = [];

        try {
            // 首先尝试批量调用后端API处理所有图片
            const batchProcessedImages = await this.batchProcessImages();
            
            if (batchProcessedImages.length > 0) {
                // 如果后端批量处理成功，使用后端结果
                this.processedImages = batchProcessedImages;
            } 
        } catch (error) {
            console.error('处理过程失败:', error);
        } finally {
            this.hideLoading();
            this.showResults();
        }
    }

    /**
     * 批量处理图片（调用后端API）
     */
    async batchProcessImages() {
        try {
            // 将所有图片转换为base64格式，同时保留文件名信息
            // 兼容两种图片来源：1. 正常上传的图片（有真实File对象） 2. 从toPS目录加载的图片（已有base64 url）
            const imagePromises = this.uploadedImages.map(image => {
                // 对于已有url（从toPS加载的图片），直接使用url
                if (image.url && image.url.startsWith('data:image/')) {
                    return Promise.resolve({
                        data: image.url,
                        filename: image.name || image.filename
                    });
                }
                // 对于正常上传的图片，使用FileReader读取
                else if (image.file && image.file instanceof Blob) {
                    return new Promise((resolve) => {
                        const reader = new FileReader();
                        reader.onload = (e) => resolve({
                            data: e.target.result,
                            filename: image.name
                        });
                        reader.readAsDataURL(image.file);
                    });
                }
                // 处理其他情况
                else {
                    console.warn('无法处理的图片数据类型:', image);
                    return Promise.resolve(null);
                }
            });

            // 过滤掉null值
            const imageResults = await Promise.all(imagePromises);
            const imagesWithNames = imageResults.filter(item => item !== null);
            
            // 如果没有可处理的图片，返回空数组
            if (imagesWithNames.length === 0) {
                console.warn('没有找到可处理的图片');
                return [];
            }

            // 调用后端批量处理API
            const response = await fetch('http://localhost:5000/api/watermark-process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    images: imagesWithNames
                })
            });

            const result = await response.json();
            
            if (result.success && result.data.processed_images.length > 0) {
                // 将后端结果转换为前端格式
                return result.data.processed_images.map((processedImage, index) => ({
                    ...this.uploadedImages[index],
                    processed: true,
                    processedUrl: processedImage.data,
                    settings: {
                        position: this.watermarkPosition,
                        size: this.watermarkSize,
                        opacity: this.watermarkOpacity,
                        margin: this.watermarkMargin
                    }
                }));
            } else {
                console.warn('后端批量处理失败，回退到前端处理');
                return [];
            }
        } catch (error) {
            console.error('批量处理失败:', error);
            return [];
        }
    }

    /**
     * 显示加载动画
     */
    showLoading() {
        document.getElementById('loadingSection').style.display = 'block';
        document.getElementById('processBtn').disabled = true;
        document.getElementById('loadingSection').classList.add('fade-in');
        this.updateProgress(0, this.uploadedImages.length);
    }

    /**
     * 隐藏加载动画
     */
    hideLoading() {
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('processBtn').disabled = false;
    }

    /**
     * 更新进度
     */
    updateProgress(current, total) {
        const percentage = (current / total) * 100;
        document.getElementById('progressFill').style.width = percentage + '%';
        document.getElementById('progressText').textContent = `${current} / ${total}`;
    }

    /**
     * 显示结果
     */
    showResults() {
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').classList.add('fade-in');
        
        const grid = document.getElementById('resultsGrid');
        grid.innerHTML = '';

        this.processedImages.forEach(image => {
            const item = document.createElement('div');
            item.className = 'result-item';
            
            if (image.processed) {
                item.innerHTML = `
                    <img src="${image.processedUrl}" alt="${image.name}" class="result-image">
                `;
            } else {
                item.innerHTML = `
                    <div style="padding: 40px; text-align: center; color: #f44336;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">❌</div>
                        <div>处理失败</div>
                        <div style="font-size: 0.9rem; margin-top: 5px;">${image.error || '未知错误'}</div>
                    </div>
                `;
            }
            
            grid.appendChild(item);
        });
    }



    /**
     * 清空所有图片
     */
    clearAllImages() {
        if (confirm('确定要清空所有图片吗？')) {
            this.uploadedImages = [];
            this.processedImages = [];
            this.renderPreview();
            this.hidePreviewSection();
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('fileInput').value = '';
        }
    }

    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * 更新UI状态
     */
    updateUI() {
        const hasImages = this.uploadedImages.length > 0;
        document.getElementById('processBtn').disabled = !hasImages;
    }
}

// 初始化工具
const pEditTool = new PEditTool();

// 添加一些便利函数
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#667eea'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1001;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-in';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 添加淡出动画
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100%); }
    }
`;
document.head.appendChild(style);