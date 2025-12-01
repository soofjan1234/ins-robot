// 整理页面功能
class ImageOrganizer {
    constructor() {
        this.images = [];
        this.initializeEventListeners();
        // 页面加载时自动加载图片
        this.autoLoadImages();
    }

    initializeEventListeners() {
        document.getElementById('generateAllBtn').addEventListener('click', () => this.generateAllAIText());
        document.getElementById('organizeBtn').addEventListener('click', () => this.organizeImages());
    }

    async loadImages() {
        const status = document.getElementById('loadingStatus');
        status.textContent = '正在加载图片...';

        try {
            const response = await fetch('/api/load-to-refine');
            const result = await response.json();
            
            if (result.success) {
                this.images = result.data.images;
                status.textContent = `成功加载 ${this.images.length} 张图片`;
                
                this.displayImageNames();
            } else {
                status.textContent = '加载失败: ' + result.message;
            }
        } catch (error) {
            console.error('加载图片失败:', error);
            status.textContent = '加载失败: 网络错误';
        }
    }

    displayImageNames() {
        const namesList = document.getElementById('imageNamesList');
        namesList.innerHTML = '<h3>图片列表</h3>';
        
        const listContainer = document.createElement('div');
        listContainer.className = 'names-list-container';
        
        this.images.forEach((image, index) => {
            const nameItem = document.createElement('div');
            nameItem.className = 'name-item';
            nameItem.innerHTML = `
                <span class="image-index">${index + 1}.</span>
                <span class="image-filename">${image.filename}</span>
            `;
            listContainer.appendChild(nameItem);
        });
        
        namesList.appendChild(listContainer);
    }

    async generateAllAIText() {
        const btn = document.getElementById('generateAllBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="loading"></span> 生成中...';

        try {
            // 获取所有图片名称
            const imageNames = this.images.map(img => img.filename);
            
            // 调用AI文案生成API - 使用预设主题，无需用户输入
            const response = await fetch('/api/generate-ai-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_names: imageNames
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 将生成的文案填充到输入框
                const texts = result.texts;
                for (let i = 0; i < texts.length && i < 5; i++) {
                    const input = document.getElementById(`textInput${i + 1}`);
                    if (input) {
                        input.value = texts[i];
                    }
                }
                alert('AI文案生成成功！已自动生成5条文案并填入输入框');
            } else {
                alert('生成失败: ' + result.message);
            }
        } catch (error) {
            console.error('生成AI文案失败:', error);
            alert('生成失败: 网络错误');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '生成AI文案';
        }
    }

    async organizeImages() {
        const status = document.getElementById('organizeStatus');
        const btn = document.getElementById('organizeBtn');
        
        // 收集5个输入框的文案
        const texts = [];
        for (let i = 1; i <= 5; i++) {
            const input = document.getElementById(`textInput${i}`);
            if (input && input.value.trim()) {
                texts.push(input.value.trim());
            }
        }
        
        if (texts.length === 0) {
            status.textContent = '请至少输入一个文案';
            return;
        }
        
        if (this.images.length === 0) {
            status.textContent = '没有可整理的图片';
            return;
        }
        
        btn.disabled = true;
        status.textContent = '正在整理中...';
        
        try {
            // 获取图片名称列表（只取前5个）
            const imageNames = this.images.slice(0, 5).map(img => img.filename);
            
            const response = await fetch('/api/organize-images', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_names: imageNames,
                    texts: texts
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                status.innerHTML = `
                    <div style="color: #28a745;">
                        <strong>整理成功！</strong><br>
                        已整理 ${result.data.total_organized} 个文件<br>
                        使用的文件夹: ${result.data.weekdays_used.join(', ')}<br>
                        每个文件夹包含一张图片和一个文案文件
                    </div>
                `;
                alert('整理完成！图片和文案已分布到各星期文件夹中');
            } else {
                status.innerHTML = `<div style="color: #dc3545;">整理失败: ${result.message}</div>`;
            }
        } catch (error) {
            console.error('整理失败:', error);
            status.innerHTML = '<div style="color: #dc3545;">整理失败: 网络错误</div>';
        } finally {
            btn.disabled = false;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 页面加载时自动加载图片
    async autoLoadImages() {
        // 延迟一点加载，让页面先渲染出来
        setTimeout(() => {
            this.loadImages();
        }, 500);
    }
}

// 初始化页面
const organizer = new ImageOrganizer();