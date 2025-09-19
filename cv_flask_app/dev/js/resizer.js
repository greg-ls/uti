function setupResizer() {
    const resizer = document.getElementById('resizer');
    const editorSection = document.getElementById('editorSection');
    const assistantPanel = document.getElementById('assistantPanel');
    
    if (!resizer) return;
    
    let isResizing = false;
    
    resizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        document.body.classList.add('no-select');
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        const containerWidth = document.getElementById('mainContainer').offsetWidth;
        const newWidth = (e.clientX / containerWidth) * 100;
        
        if (newWidth > 30 && newWidth < 70) {
            editorSection.style.width = newWidth + '%';
            assistantPanel.style.width = (100 - newWidth) + '%';
        }
    });
    
    document.addEventListener('mouseup', function() {
        isResizing = false;
        document.body.classList.remove('no-select');
    });
}

function setupChatResizer() {
    // Placeholder pour le redimensionnement du chat
    console.log('Chat resizer initialized');
}