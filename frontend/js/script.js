document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const editBtn = document.getElementById('edit-btn');
    const organizeBtn = document.getElementById('organize-btn');
    const publishBtn = document.getElementById('publish-btn');

    generateBtn.addEventListener('click', function() {
        console.log('生图功能被点击');
        alert('生图功能开发中...');
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
});