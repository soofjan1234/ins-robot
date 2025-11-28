document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const editBtn = document.getElementById('edit-btn');
    const organizeBtn = document.getElementById('organize-btn');
    const publishBtn = document.getElementById('publish-btn');
    const cleanBtn = document.getElementById('clean-btn');

    generateBtn.addEventListener('click', function() {
        console.log('生图功能被点击');
        window.location.href = 'generate.html';
    });

    editBtn.addEventListener('click', function() {
        console.log('P图功能被点击');
        window.location.href = 'pedit.html';
    });

    organizeBtn.addEventListener('click', function() {
        console.log('整理功能被点击');
        window.location.href = 'organize.html';
    });

    publishBtn.addEventListener('click', function() {
        console.log('发布功能被点击');
        window.location.href = 'publish.html';
    });

    cleanBtn.addEventListener('click', function() {
        console.log('清理功能被点击');
        
        // 显示确认对话框
        if (!confirm('确定要清理所有临时文件吗？这将删除所有生成的图片和文本文件。')) {
            return;
        }
        
        // 禁用按钮，防止重复点击
        cleanBtn.disabled = true;
        cleanBtn.style.opacity = '0.6';
        cleanBtn.innerHTML = '清理中...';
        
        // 调用清理API
        fetch('http://localhost:5000/api/clean-files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('清理API响应:', data);
            
            if (data.success) {
                // 显示成功消息，包含详细信息
                let message = `清理完成！\n\n`;
                message += `总共清理: ${data.data.total_files_cleaned} 个文件\n`;
                message += `图片: ${data.data.total_image_files_cleaned} 个\n`;
                message += `文本: ${data.data.total_text_files_cleaned} 个\n`;
                message += `释放空间: ${data.data.total_size_cleaned_mb} MB`;
                
                alert(message);
            } else {
                // 显示错误消息
                alert('清理失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('清理功能请求错误:', error);
            alert('清理请求失败，请稍后重试');
        })
        .finally(() => {
            // 恢复按钮状态
            cleanBtn.disabled = false;
            cleanBtn.style.opacity = '1';
            cleanBtn.innerHTML = '🧹 清理';
        });
    });
});