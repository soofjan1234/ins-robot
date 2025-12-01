/**
 * 生图页面JavaScript功能
 * 支持多张图片上传、AI生成和结果展示
 */

class GenerateTool {
    constructor() {
        this.uploadedImages = [];
        this.generatedImages = [];
        this.aiParams = {
            prompt: '',
            negativePrompt: '',
            steps: 30,
            cfgScale: 7,
            seed: -1,
            width: 512,
            height: 512
        };
        this.init();
        this.loadPendingImages();
    }

    /**
     * 从后端加载待生成的图片
     */
    async loadPendingImages() {
        try {
            // 显示加载动画
            this.showLoading();
            
            // 调用后端接口
            const response = await fetch('http://localhost:5000/api/load-to-generate-imgs', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const result = await response.json();
            
            if (result.success && result.data && result.data.images) {
                // 清空现有图片
                this.uploadedImages = [];
                
                // 添加从后端加载的图片
                result.data.images.forEach(imgData => {
                    // 根据文件扩展名确定MIME类型
                    const extension = imgData.filename.split('.').pop().toLowerCase();
                    const mimeTypes = {
                        'png': 'image/png',
                        'jpg': 'image/jpeg',
                        'jpeg': 'image/jpeg',
                        'gif': 'image/gif',
                        'webp': 'image/webp'
                    };
                    const mimeType = mimeTypes[extension] || 'image/png';
                    
                    // 添加data:image前缀
                    const base64Url = `data:${mimeType};base64,${imgData.data}`;
                    
                    const imageData = {
                        id: Date.now() + Math.random(),
                        file: {
                            name: imgData.filename,
                            size: imgData.size
                        },
                        name: imgData.filename,
                        size: this.formatFileSize(imgData.size),
                        url: base64Url,
                        generated: false
                    };
                    this.uploadedImages.push(imageData);
                });
                
                // 显示预览区域
                this.renderPreview();
                this.showPreviewSection();
                this.updateUI();
                
                showNotification(`成功加载 ${result.data.images.length} 张待生成图片！`, 'success');
            } else {
                const errorMessage = result.message || '加载待生成图片失败';
                this.displayError(errorMessage);
                showNotification(errorMessage, 'error');
            }
        } catch (error) {
            console.error('加载待生成图片失败:', error);
            
            // 根据错误类型显示不同的错误信息
            let errorMessage = '加载待生成图片过程中出现错误';
            if (error.message.includes('Failed to fetch')) {
                errorMessage = '网络错误，请检查后端服务是否正常运行';
            } else if (error.message.includes('timeout')) {
                errorMessage = '请求超时，请稍后重试';
            }
            
            this.displayError(errorMessage + ': ' + error.message);
            showNotification(errorMessage + '！', 'error');
        } finally {
            // 隐藏加载动画
            this.hideLoading();
        }
    }
    
    /**
     * 初始化事件监听
     */
    init() {
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
            // 直接使用已有的base64数据，不需要再次使用FileReader读取
            const imagesWithNames = this.uploadedImages.map(image => ({
                data: image.url, // 直接使用已有的base64 URL
                filename: image.name
            }));

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

        this.generatedImages.forEach((image, index) => {
            const item = document.createElement('div');
            item.className = 'result-item';
            
            if (image.generated) {
                item.innerHTML = `
                    <img src="${image.generatedUrl}" alt="生成结果" class="result-image">
                    <div class="action-buttons">
                        <button class="regenerate-btn" onclick="generateTool.regenerateImage(${index}, '${image.generatedUrl}')">
                            重新生成
                        </button>
                    </div>
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
     * 重新生成图片
     */
    async regenerateImage(index, imageUrl) {
        try {
            // 获取当前操作的结果项，添加局部加载状态
            const resultItems = document.querySelectorAll('.result-item');
            const currentItem = resultItems[index];
            
            if (currentItem) {
                // 保存原始内容用于恢复
                const originalContent = currentItem.innerHTML;
                // 添加加载状态
                currentItem.innerHTML = `
                    <div style="padding: 40px; text-align: center;">
                        <div class="loading-spinner"></div>
                        <div style="margin-top: 10px; color: #666;">正在重新生成...</div>
                    </div>
                `;
            }
            
            // 调用后端重新生成接口
            const response = await fetch('http://localhost:5000/api/regenerate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageUrl,
                    index: index
                })
            });

            // 检查响应状态
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success && result.data) {
                // 更新对应索引的图片
                this.generatedImages[index] = {
                    generated: true,
                    generatedUrl: result.data.image,
                    text_content: result.data.text_content || '',
                    filename: result.data.filename || 'regenerated_image'
                };
                
                // 重新渲染结果
                this.showResults();
                showNotification('图片重新生成成功！', 'success');
            } else {
                const errorMessage = result.message || '服务器处理错误';
                console.error('重新生成失败:', errorMessage);
                // 如果有当前项，恢复原始内容
                if (currentItem) {
                    this.showResults(); // 重新渲染所有结果，而不是只恢复一个
                }
                this.showError('图片重新生成失败: ' + errorMessage);
                showNotification('图片重新生成失败！', 'error');
            }
        } catch (error) {
            console.error('重新生成失败:', error);
            // 在全局隐藏加载状态
            this.hideLoading();
            // 重新渲染结果，确保状态正确
            this.showResults();
            
            // 根据错误类型显示不同的错误信息
            let errorMessage = '重新生成过程中出现错误';
            if (error.message.includes('Failed to fetch')) {
                errorMessage = '网络错误，请检查后端服务是否正常运行';
            } else if (error.message.includes('timeout')) {
                errorMessage = '请求超时，请稍后重试';
            }
            
            this.showError(errorMessage + ': ' + error.message);
            showNotification(errorMessage + '！', 'error');
        }
    }

    /**
     * 下载图片
     */


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
    
    /**
     * 显示错误信息
     */
    displayError(message) {
        console.error('错误:', message);
        // 可以在这里添加更复杂的错误显示逻辑，比如显示一个错误提示框
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: #f44336;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            z-index: 1002;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        `;
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            if (document.body.contains(errorDiv)) {
                document.body.removeChild(errorDiv);
            }
        }, 3000);
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
    
    .result-item .action-buttons {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 8px;
        opacity: 0;
        transition: all 0.3s ease;
    }
    
    .result-item:hover .action-buttons {
        opacity: 1;
    }
    
    .download-btn,
    .regenerate-btn {
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .download-btn:hover {
        background-color: rgba(0, 123, 255, 0.9);
    }
    
    .regenerate-btn:hover {
        background-color: rgba(255, 152, 0, 0.9);
    }
    
    .loading-spinner {
        display: inline-block;
        width: 30px;
        height: 30px;
        border: 3px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: #007bff;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
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