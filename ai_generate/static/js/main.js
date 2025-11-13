// 模式切换
const batchModeToggle = document.getElementById('batchModeToggle');
const singleMode = document.getElementById('singleMode');
const batchMode = document.getElementById('batchMode');

batchModeToggle.addEventListener('click', () => {
    singleMode.classList.toggle('hidden');
    batchMode.classList.toggle('hidden');
    
    if (batchMode.classList.contains('hidden')) {
        batchModeToggle.innerHTML = '<i class="fa fa-cubes mr-2"></i>批量模式';
    } else {
        batchModeToggle.innerHTML = '<i class="fa fa-picture-o mr-2"></i>单图模式';
    }
});

// 单图模式 - 图片上传预览
const uploadArea = document.getElementById('uploadArea');
const imageUpload = document.getElementById('imageUpload');
const selectImageBtn = document.getElementById('selectImageBtn');
const previewContainer = document.getElementById('previewContainer');
const imagePreview = document.getElementById('imagePreview');
const removeImageBtn = document.getElementById('removeImageBtn');

selectImageBtn.addEventListener('click', () => {
    imageUpload.click();
});

imageUpload.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = (event) => {
            imagePreview.src = event.target.result;
            previewContainer.classList.remove('hidden');
            uploadArea.classList.add('hidden');
        };
        reader.readAsDataURL(e.target.files[0]);
    }
});

removeImageBtn.addEventListener('click', () => {
    previewContainer.classList.add('hidden');
    uploadArea.classList.remove('hidden');
    imageUpload.value = '';
});

// 拖放功能
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('active');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('active');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('active');
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const reader = new FileReader();
        reader.onload = (event) => {
            imagePreview.src = event.target.result;
            previewContainer.classList.remove('hidden');
            uploadArea.classList.add('hidden');
        };
        reader.readAsDataURL(e.dataTransfer.files[0]);
        imageUpload.files = e.dataTransfer.files;
    }
});

// 单图生成功能
const generateBtn = document.getElementById('generateBtn');
const promptInput = document.getElementById('prompt');
const resultArea = document.getElementById('resultArea');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const imageResultContainer = document.getElementById('imageResultContainer');
const generatedImage = document.getElementById('generatedImage');
const downloadBtn = document.getElementById('downloadBtn');
const regenerateBtn = document.getElementById('regenerateBtn');
const retryBtn = document.getElementById('retryBtn');

generateBtn.addEventListener('click', generateImage);
regenerateBtn.addEventListener('click', generateImage);
retryBtn.addEventListener('click', generateImage);

downloadBtn.addEventListener('click', () => {
    const link = document.createElement('a');
    link.href = generatedImage.src;
    link.download = 'generated-image.jpg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

function generateImage() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
        alert('请输入图片描述');
        return;
    }
    
    resultArea.classList.remove('hidden');
    loadingState.classList.remove('hidden');
    errorState.classList.add('hidden');
    imageResultContainer.classList.add('hidden');
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('prompt', prompt);
    
    // 添加图片（如果有）
    if (imageUpload.files.length > 0) {
        formData.append('image', imageUpload.files[0]);
    }
    
    // 发送请求到后端API
    fetch('/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('生成失败');
        }
        return response.json();
    })
    .then(data => {
        loadingState.classList.add('hidden');
        imageResultContainer.classList.remove('hidden');
        generatedImage.src = data.image_url;
    })
    .catch(error => {
        loadingState.classList.add('hidden');
        errorState.classList.remove('hidden');
        errorMessage.textContent = error.message || '生成失败，请重试';
    });
}

// 批量模式功能
const batchGenerateBtn = document.getElementById('batchGenerateBtn');
const decreaseCountBtn = document.getElementById('decreaseCountBtn');
const increaseCountBtn = document.getElementById('increaseCountBtn');
const imageCountInput = document.getElementById('imageCount');
const batchPrompt = document.getElementById('batchPrompt');
const batchResultArea = document.getElementById('batchResultArea');
const batchLoadingState = document.getElementById('batchLoadingState');
const batchResultsGrid = document.getElementById('batchResultsGrid');

// 数量减少按钮
decreaseCountBtn.addEventListener('click', () => {
    let currentCount = parseInt(imageCountInput.value);
    if (currentCount > 1) {
        imageCountInput.value = currentCount - 1;
    }
});

// 数量增加按钮
increaseCountBtn.addEventListener('click', () => {
    let currentCount = parseInt(imageCountInput.value);
    if (currentCount < 10) {
        imageCountInput.value = currentCount + 1;
    }
});

// 确保输入值在有效范围内
imageCountInput.addEventListener('change', () => {
    let count = parseInt(imageCountInput.value);
    if (isNaN(count) || count < 1) {
        imageCountInput.value = 1;
    } else if (count > 10) {
        imageCountInput.value = 10;
    }
});

// 通知函数
function showNotification(message, type) {
    alert(message);
}

// 显示加载状态
function showLoader(message) {
    batchLoadingState.querySelector('.loading-text').textContent = message;
    batchLoadingState.classList.remove('hidden');
}

// 隐藏加载状态
function hideLoader() {
    batchLoadingState.classList.add('hidden');
}

// 显示批量生成结果
function showBatchResults(results) {
    batchResultsGrid.innerHTML = '';
    
    if (results && results.length > 0) {
        results.forEach((result, index) => {
            const resultCard = document.createElement('div');
            resultCard.className = 'bg-white rounded-lg shadow p-4 card';
            resultCard.innerHTML = `
                <div class="aspect-square bg-gray-100 rounded-md overflow-hidden mb-4">
                    <img src="${result.image_url}" alt="生成的图片 ${index + 1}" class="w-full h-full object-cover">
                </div>
                <div class="flex justify-between items-center">
                    <button class="download-batch-btn btn-secondary text-white px-3 py-1.5 rounded-lg text-sm flex items-center">
                        <i class="fa fa-download mr-1"></i>
                        下载
                    </button>
                    <span class="text-xs text-gray-500">#${index + 1}</span>
                </div>
            `;
            
            batchResultsGrid.appendChild(resultCard);
            
            // 添加下载事件
            const downloadBtn = resultCard.querySelector('.download-batch-btn');
            downloadBtn.addEventListener('click', () => {
                const link = document.createElement('a');
                link.href = result.image_url;
                link.download = `generated-image-${index + 1}.jpg`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        });
    } else {
        batchResultsGrid.innerHTML = `
            <div class="col-span-full text-center py-10">
                <i class="fa fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
                <p class="text-red-600 mb-2">没有生成图片，请重试</p>
                <button class="text-primary font-medium hover:underline" onclick="generateBatchImages()">重新生成</button>
            </div>
        `;
    }
}

batchGenerateBtn.addEventListener('click', async function generateBatchImages() {
    const prompt = batchPrompt.value.trim();
    const count = parseInt(imageCountInput.value);
    
    if (!prompt) {
        showNotification('请输入图片描述', 'error');
        return;
    }
    
    batchResultArea.classList.remove('hidden');
    batchGenerateBtn.disabled = true;
    const originalText = batchGenerateBtn.innerHTML;
    batchGenerateBtn.innerHTML = '<i class="fa fa-spinner fa-spin mr-2"></i> 生成中...';
    
    try {
        // 显示加载状态
        showLoader('正在生成图片，请稍候...');
        
        const response = await fetch('/batch-generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt, count })
        });
        
        if (!response.ok) {
            throw new Error('批量生成失败');
        }
        
        const data = await response.json();
        
        // 隐藏加载状态
        hideLoader();
        
        // 显示生成结果
        showBatchResults(data.results || data.images);
        
        // 通知用户
        showNotification('图片生成成功', 'success');
    } catch (error) {
        hideLoader();
        batchResultsGrid.innerHTML = `
            <div class="col-span-full text-center py-10">
                <i class="fa fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
                <p class="text-red-600 mb-2">${error.message || '批量生成失败，请重试'}</p>
                <button class="text-primary font-medium hover:underline" onclick="generateBatchImages()">重新生成</button>
            </div>
        `;
        showNotification('生成图片失败: ' + error.message, 'error');
    } finally {
        batchGenerateBtn.disabled = false;
        batchGenerateBtn.innerHTML = originalText;
    }
});