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
            const response = await fetch('/api/load-ps-images');
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
            // 随机选择一张图片来生成文案
            const randomIndex = Math.floor(Math.random() * this.images.length);
            const image = this.images[randomIndex];
            
            const response = await fetch('http://localhost:5000/api/generate-ai-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: image.filename,
                    image_data: image.data
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 将生成的文案放入第一个输入框
                document.getElementById('textInput1').value = result.data.text;
                alert('AI文案生成成功！已填入第一个输入框');
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
        
        btn.disabled = true;
        status.textContent = '正在整理中...';
        
        try {
            // 将文案与图片对应
            const imageTexts = {};
            this.images.forEach((image, index) => {
                if (index < texts.length) {
                    imageTexts[image.filename] = texts[index];
                }
            });
            
            const response = await fetch('/api/organize-images', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    texts: imageTexts
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                status.innerHTML = `
                    <div style="color: #28a745;">
                        <strong>整理成功！</strong><br>
                        已整理到文件夹: ${result.data.folder}<br>
                        共处理 ${result.data.count} 张图片
                    </div>
                `;
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