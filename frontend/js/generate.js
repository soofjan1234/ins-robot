/**
 * 生图页面JavaScript功能
 * 支持多张图片上传、AI生成和结果展示
 */

class GenerateTool {
    constructor() {
        this.uploadedImages = [];
        this.generatedImages = [];
        this.aiParams = {
            style: 'standard',
            resolution: '1024x1024',
            creativity: 0.7
        };
        
        this.initializeEventListeners();
    }

    /**
     * 初始化事件监听器
     */
    initializeEventListeners() {
        console.log('初始化事件监听器');

        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const processBtn = document.getElementById('processBtn');
        const clearBtn = document.getElementById('clearBtn');

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

        // AI参数控制面板
        const aiStyle = document.getElementById('aiStyle');
        const resolution = document.getElementById('resolution');
        const creativity = document.getElementById('creativity');
        if (aiStyle) aiStyle.addEventListener('change', this.updateAIParams.bind(this));
        if (resolution) resolution.addEventListener('change', this.updateAIParams.bind(this));
        if (creativity) creativity.addEventListener('input', this.updateAIParams.bind(this));

        if (processBtn) processBtn.addEventListener('click', this.startGenerating.bind(this));
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
                generated: false
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
        if (!grid) return;
        
        grid.innerHTML = '';

        this.uploadedImages.forEach((image, index) => {
            const item = document.createElement('div');
            item.className = 'image-item';
            item.innerHTML = `
                <img src="${image.url}" alt="${image.name}" loading="lazy">
                <div class="image-item-info">
                    <div class="image-name">${this.truncateText(image.name, 15)}</div>
                    <div class="image-size">${image.size}</div>
                </div>
                <button class="remove-image" onclick="generateTool.removeImage(${image.id})" title="移除图片">&times;</button>
            `;
            
            // 添加动画效果
            item.style.animation = `slideIn 0.3s ease-out ${index * 0.1}s`;
            item.style.animationFillMode = 'both';
            
            grid.appendChild(item);
        });
    }

    /**
     * 截断文本
     */
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
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
            this.hideResultsSection();
        }
    }

    /**
     * 更新AI参数设置
     */
    updateAIParams() {
        const aiStyle = document.getElementById('aiStyle');
        const resolution = document.getElementById('resolution');
        const creativity = document.getElementById('creativity');
        const creativityValue = document.getElementById('creativityValue');
        
        if (aiStyle) this.aiParams.style = aiStyle.value;
        if (resolution) this.aiParams.resolution = resolution.value;
        if (creativity) {
            this.aiParams.creativity = parseFloat(creativity.value);
            if (creativityValue) {
                creativityValue.textContent = Math.round(this.aiParams.creativity * 100) + '%';
            }
        }
    }

    /**
     * 开始生成图片
     */
    async startGenerating() {
        if (this.uploadedImages.length === 0) {
            showNotification('请先上传图片！', 'error');
            return;
        }

        this.showLoading();
        this.generatedImages = [];

        try {
            const generatedImages = await this.batchGenerateImages();
            
            if (generatedImages && generatedImages.length > 0) {
                this.generatedImages = generatedImages;
            } else {
                showNotification('批量生成失败，请稍后再试或检查服务器日志。', 'error');
                this.generatedImages = []; // 清空可能存在的旧数据
            }
        } catch (error) {
            console.error('生成过程失败:', error);
            showNotification('生成过程中出现错误！', 'error');
        } finally {
            this.hideLoading();
            this.showResults();
        }
    }

    /**
     * 批量生成图片（调用后端API）
     */
    async batchGenerateImages() {
        try {
            // 将所有图片转换为base64格式，同时保留文件名信息
            const imagePromises = this.uploadedImages.map(image => {
                return new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve({
                        data: e.target.result,
                        filename: image.name
                    });
                    reader.readAsDataURL(image.file);
                });
            });

            const imagesWithNames = await Promise.all(imagePromises);

            // 调用后端批量生成API
            // 显示加载状态
            this.showLoading();
            
            const response = await fetch('http://localhost:5000/api/ai-generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    images: imagesWithNames,
                })
            });

            const result = await response.json();
        
            // 隐藏加载状态
            this.hideLoading();
            
            // 构建生成结果数组
            const generatedResults = [];
            
            if (result.success && result.results) {
                // 处理每个结果
                for (const item of result.results) {
                    if (item.success && item.data) {
                        generatedResults.push({
                            generated: true,
                            generatedUrl: item.data.image,
                            text_content: item.data.text_content || '',
                            filename: item.data.filename || 'generated_image'
                        });
                    }
                }
                return generatedResults;
            } else {
                console.warn('AI图片生成失败:', result.message || '未知错误');
                this.showError('AI图片生成失败: ' + (result.message || '服务器处理错误'));
                return [];
            }
        } catch (error) {
            console.error('批量生成失败:', error);
            return [];
        }
    }

    /**
     * 显示加载动画
     */
    showLoading() {
        const loadingSection = document.getElementById('loadingSection');
        const processBtn = document.getElementById('processBtn');
        
        if (loadingSection) {
            loadingSection.style.display = 'block';
            loadingSection.classList.add('fade-in');
        }
        if (processBtn) processBtn.disabled = true;
        
        this.updateProgress(0, this.uploadedImages.length);
    }

    /**
     * 隐藏加载动画
     */
    hideLoading() {
        const loadingSection = document.getElementById('loadingSection');
        const processBtn = document.getElementById('processBtn');
        
        if (loadingSection) loadingSection.style.display = 'none';
        if (processBtn) processBtn.disabled = false;
    }

    /**
     * 更新进度
     */
    updateProgress(current, total) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (progressFill && progressText) {
            const percentage = (current / total) * 100;
            progressFill.style.width = percentage + '%';
            progressText.textContent = `${current} / ${total}`;
        }
    }

    /**
     * 显示结果
     */
    showResults() {
        const resultsSection = document.getElementById('resultsSection');
        const resultsGrid = document.getElementById('resultsGrid');
        
        if (!resultsSection || !resultsGrid) return;
        
        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');
        
        resultsGrid.innerHTML = '';

        this.generatedImages.forEach(image => {
            const item = document.createElement('div');
            item.className = 'result-item';
            
            if (image.generated) {
                item.innerHTML = `
                    <img src="${image.generatedUrl}" alt="生成结果" class="result-image">
                    <button class="download-btn" onclick="generateTool.downloadImage('${image.generatedUrl}')">
                        下载
                    </button>
                `;
            } else {
                item.innerHTML = `
                    <div style="padding: 40px; text-align: center; color: #f44336;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">❌</div>
                        <div>生成失败</div>
                        <div style="font-size: 0.9rem; margin-top: 5px;">${image.error || '未知错误'}</div>
                    </div>
                `;
            }
            
            resultsGrid.appendChild(item);
        });
    }

    /**
     * 下载图片
     */
    downloadImage(imageUrl) {
        const a = document.createElement('a');
        a.href = imageUrl;
        a.download = `generated-image-${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        showNotification('图片下载成功！', 'success');
    }

    /**
     * 显示预览区域
     */
    showPreviewSection() {
        const previewSection = document.getElementById('previewSection');
        const controlsSection = document.getElementById('controlsSection');
        
        if (previewSection) {
            previewSection.style.display = 'block';
            previewSection.classList.add('fade-in');
        }
        if (controlsSection) {
            controlsSection.style.display = 'block';
            controlsSection.classList.add('fade-in');
        }
    }

    /**
     * 隐藏预览区域
     */
    hidePreviewSection() {
        const previewSection = document.getElementById('previewSection');
        const controlsSection = document.getElementById('controlsSection');
        
        if (previewSection) previewSection.style.display = 'none';
        if (controlsSection) controlsSection.style.display = 'none';
    }

    /**
     * 隐藏结果区域
     */
    hideResultsSection() {
        const resultsSection = document.getElementById('resultsSection');
        
        if (resultsSection) resultsSection.style.display = 'none';
    }

    /**
     * 清空所有图片
     */
    clearAllImages() {
        if (confirm('确定要清空所有图片吗？')) {
            this.uploadedImages = [];
            this.generatedImages = [];
            this.renderPreview();
            this.hidePreviewSection();
            this.hideResultsSection();
            
            const fileInput = document.getElementById('fileInput');
            if (fileInput) fileInput.value = '';
            
            showNotification('已清空所有图片', 'info');
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
        const processBtn = document.getElementById('processBtn');
        
        if (processBtn) processBtn.disabled = !hasImages;
    }
}

// 页面加载完成后初始化工具
let generateTool;
document.addEventListener('DOMContentLoaded', () => {
    generateTool = new GenerateTool();
});

// 添加通知功能
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

// 添加必要的CSS样式
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100%); }
    }
    
    .upload-area.dragover {
        border-color: #007bff;
        background-color: #f0f7ff;
    }
    
    .image-item {
        position: relative;
        overflow: hidden;
        border-radius: 8px;
    }
    
    .result-item {
        position: relative;
        overflow: hidden;
        border-radius: 8px;
    }
    
    .download-btn {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        opacity: 0;
        transition: all 0.3s ease;
        font-size: 14px;
        font-weight: 500;
    }
    
    .result-item:hover .download-btn {
        opacity: 1;
        background-color: rgba(0, 123, 255, 0.9);
    }
    
    .remove-image {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        font-size: 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: all 0.3s ease;
    }
    
    .image-item:hover .remove-image {
        opacity: 1;
        background-color: rgba(244, 67, 54, 0.8);
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);